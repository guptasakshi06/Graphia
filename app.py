"""Local Streamlit UI for contract-v1 modules. Run: streamlit run app.py.

Image/OCR imports are delayed until Analyze. There is no fake OCR fallback;
all development providers live exclusively in tests/test_ui.py.
"""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError
import streamlit as st

from modules.classification import classify_document
from modules.extraction import extract_fields
from modules.readiness import TYPE_NAMES, analyze_readiness, render_report


ROOT = Path(__file__).resolve().parent
ENGINE = {"lang": "eng", "psm": 6, "timeout": 20}
BILINGUAL_ENGINE = {**ENGINE, "lang": "eng+hin", "psm": 4}
STAGES = ("original", "grayscale", "denoised", "enhanced", "thresholded", "morphology")


def collect_uploads(files):
    """Snapshot getvalue() bytes; index + hash preserves same-name duplicates."""
    items = []
    for index, upload in enumerate(files):
        data = upload.getvalue()
        digest = sha256(upload.name.encode("utf-8") + b"\0" + data).hexdigest()
        items.append({"id": f"{index}-{digest}", "filename": upload.name, "data": data})
    return items


def input_signature(items, options, required_types, source, config, *, bilingual=False):
    """Changing any analysis input makes the old report invalid."""
    payload = {"uploads": [item["id"] for item in items], "options": options,
               "required_types": required_types, "source": source, "config": config,
               "bilingual": bilingual}
    return sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()


def invalidate_results(state, signature):
    """Return whether inputs changed, discarding arrays and downloads together."""
    changed = state.get("analysis_signature") != signature
    if changed:
        state.pop("analysis", None)
        state["analysis_signature"] = signature
    return changed


def load_real_provider():
    """Only these owner-provided APIs may process production uploads."""
    from modules.preprocessing import load_image, run_pipeline
    from modules.ocr import extract_text
    return load_image, run_pipeline, extract_text


def error_ocr(message, engine=ENGINE):
    return {"text": "", "status": "error", "confidence": None,
            "error": message, "engine_config": dict(engine)}


def call_ocr(extract_text, image, engine=ENGINE):
    """Convert a raised engine error to the contracted explicit error state."""
    try:
        return extract_text(image, **engine)
    except Exception as error:
        return error_ocr(f"OCR failed: {error}", engine)


def analyze_uploads(items, options, source, provider, *, bilingual=False):
    """Orchestrate real APIs; keep every failed file and keep arrays separate.

    The provider argument makes boundary checks possible in tests. main() always
    obtains it from load_real_provider(), with no user-selectable test mode.
    """
    load_image, run_pipeline, extract_text = provider
    engine = BILINGUAL_ENGINE if bilingual else ENGINE
    records, views = [], {}
    for item in items:
        original = error_ocr("Image could not be loaded.", engine)
        processed = error_ocr("Processing did not run.", engine)
        parameters = {"requested_options": dict(options), "max_dimension": 1800}
        view = {"stages": {}, "error": None}
        try:
            image = load_image(item["data"], max_dimension=1800)
            view["stages"]["original"] = image
            parameters["loaded_dimensions"] = {"width": int(image.shape[1]), "height": int(image.shape[0])}
        except Exception as error:
            view["error"] = f"Image load failed: {error}"
            original = processed = error_ocr(view["error"], engine)
        else:
            # Original OCR is independent: pipeline failure must not erase it.
            original = call_ocr(extract_text, image, engine)
            try:
                pipeline = run_pipeline(image, options=dict(options))
                if not set(STAGES).issubset(pipeline["stages"]):
                    raise ValueError("Pipeline did not return all six named stages.")
                parameters["resolved_pipeline"] = pipeline["parameters"]
                view["stages"] = pipeline["stages"]
                processed = call_ocr(extract_text, pipeline["ocr_input"], engine)
            except Exception as error:
                view["error"] = f"Processing failed: {error}"
                processed = error_ocr(view["error"], engine)
        selected_source = "original" if source == "original" else "processed"
        selected = original if selected_source == "original" else processed
        if source == "auto" and "original" in view["stages"]:
            from modules.photo_ocr import recover_photo

            selected_source, selected, classification, fields, method = recover_photo(
                image, original, processed,
                lambda pixels, settings: call_ocr(extract_text, pixels, settings), engine,
            )
            if selected_source == "processed":
                processed = selected
            parameters["photo_recovery"] = method
        else:
            classification = classify_document(selected["text"])
            fields = extract_fields(selected["text"], classification["doc_type"])
        records.append({
            "id": item["id"], "filename": item["filename"],
            "ocr_original": original, "ocr_processed": processed, "ocr_source": selected_source,
            "ocr": selected, "classification": classification,
            "fields": fields,
            "processing_parameters": parameters,
        })
        views[item["id"]] = view
    return records, views


def display_pixels(image):
    """OpenCV BGR → RGB; a 2-D grayscale image keeps its values."""
    return image[:, :, ::-1] if image.ndim == 3 else image


def preview_upload(data):
    """Small display-only Pillow preview; processing still uses load_image bytes."""
    with Image.open(BytesIO(data)) as image:
        image = ImageOps.exif_transpose(image).convert("RGBA")
        image.thumbnail((900, 900))
        background = Image.new("RGBA", image.size, "white")
        return Image.alpha_composite(background, image).convert("RGB")


def processing_controls():
    """Expose contract-v1 options, including valid odd kernels/block sizes."""
    with st.expander("Processing settings", expanded=False):
        st.caption("Choose alternatives; these settings are not a promise of better OCR. "
                   "All named stages remain visible when an operation is bypassed.")
        denoise = st.selectbox("Denoising", ["median", "gaussian", "none"])
        kernel = st.select_slider("Denoising kernel (odd pixels)", [1, 3, 5, 7, 9], value=3)
        contrast = st.selectbox("Contrast", ["clahe", "equalize", "none"])
        threshold = st.selectbox("Threshold", ["otsu", "global", "adaptive", "none"])
        global_value = st.slider("Global threshold (0–255)", 0, 255, 127)
        block = st.select_slider("Adaptive block size (odd pixels)", [3, 5, 11, 21, 31, 51], value=31)
        adaptive_c = st.number_input("Adaptive C", value=11.0, step=1.0)
        morphology = st.selectbox("Morphology", ["none", "erosion", "dilation", "opening", "closing"])
        morph_kernel = st.slider("Morphology kernel (pixels)", 1, 7, 2)
        st.caption("Median replaces a pixel by its neighbourhood median; Gaussian smooths "
                   "with weighted neighbours. Thresholding separates dark and light pixels. "
                   "Morphology changes the foreground shape; compare before choosing it.")
    return {"denoise": denoise, "kernel_size": kernel, "contrast": contrast,
            "threshold": threshold, "global_threshold": global_value,
            "adaptive_block_size": block, "adaptive_c": adaptive_c,
            "morphology": morphology, "morph_kernel_size": morph_kernel}


def show_results(result):
    report, views = result["report"], result["views"]
    st.subheader("Readiness analysis")
    st.write("Overall status: " + report["overall_status"])
    columns = st.columns(3)
    columns[0].metric("Submitted files", report["submitted_file_count"])
    columns[1].metric("Detected required types", report["detected_required_type_count"])
    columns[2].metric("Usable required types", report["usable_required_type_count"])
    st.caption(f"Required types: {report['required_type_count']}. Duplicate types count once.")
    columns = st.columns(2)
    columns[0].metric("Coverage", f"{report['coverage_percent']:.2f}%")
    columns[1].metric("Readiness", f"{report['readiness_percent']:.2f}%")
    st.write("Missing types: " + (", ".join(TYPE_NAMES[x] for x in report["missing_types"]) or "None"))
    st.write("Detected but unusable types: " + (", ".join(TYPE_NAMES[x] for x in report["unusable_types"]) or "None"))
    for document in report["documents"]:
        with st.expander("File: " + document["filename"], expanded=True):
            st.caption("Record ID: " + document["id"])
            view = views[document["id"]]
            if view["error"]:
                st.error(view["error"])
            st.write("Detected type: " + TYPE_NAMES[document["doc_type"]])
            st.write("Matched keywords:")
            st.json(document["classification"])
            st.write(f"Readable heuristic: {document['readable']} · Usable candidate: {document['usable']}")
            if document["problems"]:
                st.warning("\n".join(document["problems"]))
            st.write("Extracted fields (selected OCR: " + document["ocr_source"] + ")")
            photo_method = document["processing_parameters"].get("photo_recovery")
            if photo_method:
                st.caption("Auto photo selected " + photo_method + ".")
            st.json({key: value if value is not None else "Not Found / Unreadable"
                     for key, value in document["fields"].items()})
            st.write("Original and processed OCR")
            for column, source in zip(st.columns(2), ("original", "processed")):
                ocr = document["ocr_" + source]
                column.write(source.title() + " — " + ocr["status"])
                column.code(ocr["text"] or "No usable OCR text", language=None)
                if ocr["error"]:
                    column.error(ocr["error"])
                column.caption(f"Engine settings: {ocr['engine_config']}; "
                               f"confidence heuristic: {ocr['confidence']} (not accuracy)")
            st.write("Named image processing views")
            for stage in STAGES:
                if stage in view["stages"]:
                    st.image(display_pixels(view["stages"][stage]), caption=stage.title(), width="stretch")
            st.write("Requested settings, resolved pipeline and loaded dimensions")
            st.json(document["processing_parameters"])
    st.download_button("Download JSON report", json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False),
                       file_name="readiness_report.json", mime="application/json", on_click="ignore")
    st.download_button("Download Markdown report", render_report(report),
                       file_name="readiness_report.md", mime="text/markdown", on_click="ignore")
    with st.expander("Readable report"):
        st.markdown(render_report(report))


def main():
    st.set_page_config(page_title="Document Intelligence — Project 042", layout="wide")
    st.title("Document Intelligence for Application Readiness")
    st.caption("Project 042 · Sakshi Gupta and Jigisha Baiswar · Local academic demonstration")
    st.info("Local DIP and Tesseract OCR process your uploaded images. "
            "Compare the original and processed OCR before reviewing readiness.")
    st.write("Upload JPG, JPEG or PNG documents, choose a checklist and processing settings, "
             "then press Analyze documents. Review both OCR outputs before choosing a source.")
    st.warning("Demonstration checklist only. Readiness checks presence and usable information; "
               "it does not verify authenticity, official eligibility or matching student identity.")
    st.caption("Uploads stay in this session; the app does not save them to disk. "
               "Download a report only when you want a local copy.")
    try:
        config = json.loads((ROOT / "config/requirements.json").read_text(encoding="utf-8"))
        analyze_readiness([], config)  # Validate policy before building widgets.
    except (OSError, ValueError) as error:
        st.session_state.pop("analysis", None)
        st.error(f"Checklist configuration error: {error}")
        return
    required = st.multiselect("Required document types", list(config["required_documents"]),
                              default=list(config["required_documents"]), format_func=TYPE_NAMES.get)
    st.caption(f"Readability heuristic: OCR status ok and at least "
               f"{config['readability']['min_alnum_chars']} alphanumeric characters. "
               "Each required type needs one file with its configured fields.")
    with st.expander("Configured required fields"):
        st.json({TYPE_NAMES[key]: config["required_documents"][key] for key in required})
    options = processing_controls()
    bilingual = st.selectbox(
        "OCR language", ["English", "English + Hindi"],
        help="Choose English + Hindi for bilingual forms. If the processed text is "
             "less readable, select original as the OCR source.",
    ) == "English + Hindi"
    source = st.radio(
        "OCR source used for type, fields and readiness", ["processed", "original", "auto"],
        format_func=lambda value: "Auto photo" if value == "auto" else value,
        horizontal=True,
        help="Auto photo tries to crop the page and correct sideways photos when the standard OCR misses fields.",
    )
    uploads = st.file_uploader("Document images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    items = collect_uploads(uploads)
    signature = input_signature(items, options, required, source, config, bilingual=bilingual)
    had_results = "analysis" in st.session_state
    if invalidate_results(st.session_state, signature) and had_results:
        st.info("Inputs changed. Previous results and downloads were cleared; press Analyze documents again.")
    for item in items:
        with st.expander("Upload preview: " + item["filename"]):
            try:
                st.image(preview_upload(item["data"]), caption=item["filename"], width="stretch")
            except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError) as error:
                st.error(f"Cannot preview this image: {error}. Analyze will retain its error record.")
    if not required:
        st.error("Select at least one required document type.")
    if st.button("Analyze documents", disabled=not items or not required, type="primary"):
        st.session_state.pop("analysis", None)
        try:
            provider = load_real_provider()
        except (ImportError, OSError) as error:
            st.error(f"Awaiting real DIP/OCR modules: {error}. Check the local installation and module files; no fake OCR fallback is used.")
        else:
            try:
                with st.spinner("Processing images and running original/processed OCR…"):
                    records, views = analyze_uploads(items, options, source, provider, bilingual=bilingual)
                    report = analyze_readiness(records, config, required)
                    st.session_state["analysis"] = {"report": report, "views": views}
            except Exception as error:
                st.session_state.pop("analysis", None)
                st.error(f"Analysis could not complete: {error}")
    if "analysis" in st.session_state:
        show_results(st.session_state["analysis"])
    elif not items:
        st.info("Upload at least one document image to begin.")


if __name__ == "__main__":
    main()
