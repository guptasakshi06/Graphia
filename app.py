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
FIELD_NAMES = {
    "student_name": "Name",
    "certificate_number": "Certificate number",
    "application_id": "Application ID",
    "issue_date": "Issue date",
}
OCR_SOURCES = {"processed": "Processed", "original": "Original", "auto": "Auto photo"}


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
    with st.expander("Advanced image settings"):
        st.caption("Adjust the processing pipeline and compare the results in Image stages.")
        denoise = st.selectbox("Denoising", ["median", "gaussian", "none"])
        kernel = st.select_slider("Denoising kernel (odd pixels)", [1, 3, 5, 7, 9], value=3)
        contrast = st.selectbox("Contrast", ["clahe", "equalize", "none"])
        threshold = st.selectbox("Threshold", ["otsu", "global", "adaptive", "none"])
        global_value = st.slider("Global threshold (0–255)", 0, 255, 127)
        block = st.select_slider("Adaptive block size (odd pixels)", [3, 5, 11, 21, 31, 51], value=31)
        adaptive_c = st.number_input("Adaptive C", value=11.0, step=1.0)
        morphology = st.selectbox("Morphology", ["none", "erosion", "dilation", "opening", "closing"])
        morph_kernel = st.slider("Morphology kernel (pixels)", 1, 7, 2)
    return {"denoise": denoise, "kernel_size": kernel, "contrast": contrast,
            "threshold": threshold, "global_threshold": global_value,
            "adaptive_block_size": block, "adaptive_c": adaptive_c,
            "morphology": morphology, "morph_kernel_size": morph_kernel}


def show_document(document, view):
    """Present one file at a time and keep raw evidence within reach."""
    doc_type = TYPE_NAMES[document["doc_type"]]
    file_status = "Usable for the checklist" if document["usable"] else "Needs review"
    if not document["is_required"]:
        file_status = "Outside the checklist" if document["doc_type"] != "unknown" else "Needs review"
    st.markdown(f"**{doc_type}** · {file_status}")

    fields_tab, ocr_tab, images_tab = st.tabs(["Extracted fields", "OCR text", "Image stages"])
    with fields_tab:
        if view["error"]:
            st.error(view["error"])
        if document["problems"]:
            problems = [problem for problem in document["problems"]
                        if not problem.startswith("Missing required fields: ")]
            if document["missing_required_fields"]:
                missing = ", ".join(FIELD_NAMES[key] for key in document["missing_required_fields"])
                problems.append(f"Missing required fields: {missing}.")
            st.warning("\n".join(f"- {problem}" for problem in problems))
        st.table(
            [{"Field": FIELD_NAMES[key], "Value": value or "Not Found / Unreadable"}
             for key, value in document["fields"].items()],
            hide_index=True,
            border="horizontal",
        )
    with ocr_tab:
        photo_method = document["processing_parameters"].get("photo_recovery")
        selected_source = OCR_SOURCES[document["ocr_source"]]
        st.caption(f"OCR used for extraction: {photo_method or selected_source}")
        for column, source in zip(st.columns(2), ("original", "processed")):
            ocr = document["ocr_" + source]
            title = "Photo recovery" if source == "processed" and photo_method not in (
                None, "original", "processed"
            ) else OCR_SOURCES[source]
            with column:
                st.markdown(f"**{title}**")
                st.code(ocr["text"] or "No usable OCR text", language=None, wrap_lines=True)
                if ocr["error"]:
                    st.error(ocr["error"])
        with st.expander("Technical details"):
            st.json({
                "classification": document["classification"],
                "original_ocr": document["ocr_original"]["engine_config"],
                "processed_ocr": document["ocr_processed"]["engine_config"],
                "processing": document["processing_parameters"],
            })
    with images_tab:
        stages = [stage for stage in STAGES if stage in view["stages"]]
        if stages:
            stage = st.selectbox("Image stage", stages, index=len(stages) - 1, format_func=str.title)
            if stage == "original":
                st.image(display_pixels(view["stages"][stage]), caption="Original", width=760)
            else:
                original, processed = st.columns(2)
                original.image(display_pixels(view["stages"]["original"]), caption="Original", width="stretch")
                processed.image(display_pixels(view["stages"][stage]), caption=stage.title(), width="stretch")
                st.caption("A stage can look unchanged when its operation is turned off in the DIP settings.")
        else:
            st.caption("Image stages are unavailable for this file.")


def show_results(result):
    report, views = result["report"], result["views"]
    with st.container(border=True, key="results"):
        title, exports = st.columns([1, 2], vertical_alignment="center")
        with title:
            st.subheader("Results", anchor="graphia-results")
        with exports:
            with st.container(horizontal=True, horizontal_alignment="right"):
                st.download_button(
                    "Download JSON report", json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False),
                    file_name="readiness_report.json", mime="application/json", on_click="ignore",
                )
                st.download_button(
                    "Download Markdown report", render_report(report),
                    file_name="readiness_report.md", mime="text/markdown", on_click="ignore",
                )

        status = report["overall_status"]
        status_message = {
            "Ready": st.success,
            "Incomplete": st.info,
            "Needs Attention": st.warning,
        }[status]
        status_message(f"Overall status: {status}")
        files, coverage, readiness = st.columns(3)
        files.metric("Files reviewed", report["submitted_file_count"], border=True)
        coverage.metric("Coverage", f"{report['coverage_percent']:.2f}%", border=True,
                        help="Share of required document types detected.")
        readiness.metric("Readiness", f"{report['readiness_percent']:.2f}%", border=True,
                         help="Share of required document types with readable required fields.")
        st.caption(f"{report['usable_required_type_count']} of {report['required_type_count']} required types usable")
        if report["missing_types"]:
            st.write("Missing: " + ", ".join(TYPE_NAMES[key] for key in report["missing_types"]))
        if report["unusable_types"]:
            st.write("Detected but unusable: " + ", ".join(TYPE_NAMES[key] for key in report["unusable_types"]))

    with st.container(border=True, key="review"):
        st.subheader("Document review")
        documents = report["documents"]
        filenames = [document["filename"] for document in documents]
        labels = [
            f"{filename} (file {index + 1})" if filenames.count(filename) > 1 else filename
            for index, filename in enumerate(filenames)
        ]
        selected = st.selectbox("Document", range(len(documents)), format_func=labels.__getitem__)
        document = documents[selected]
        show_document(document, views[document["id"]])

    with st.expander("Report preview"):
        st.markdown(render_report(report))


def use_phone_photo_settings():
    """Apply the existing bilingual OCR and photo recovery options together."""
    st.session_state["ocr_language"] = "English + Hindi"
    st.session_state["ocr_source"] = "auto"


def main():
    st.set_page_config(page_title="Graphia", layout="wide")
    st.html(ROOT / ".streamlit" / "graphia.css")
    with st.container(key="page-heading"):
        st.title("Graphia")
        st.write("Review document images against a checklist.")

    try:
        config = json.loads((ROOT / "config/requirements.json").read_text(encoding="utf-8"))
        analyze_readiness([], config)
    except (OSError, ValueError) as error:
        st.session_state.pop("analysis", None)
        st.error(f"Checklist configuration error: {error}")
        return

    upload_column, settings_column = st.columns([5, 4], gap="medium")
    with upload_column, st.container(border=True, key="upload"):
        st.subheader("Add documents")
        uploads = st.file_uploader(
            "Document images", type=["jpg", "jpeg", "png"], accept_multiple_files=True,
            label_visibility="collapsed",
        )
        items = collect_uploads(uploads)
        action = st.empty()
        upload_feedback = st.empty()
        if items:
            with st.expander("Preview uploads"):
                index = st.selectbox("Preview file", range(len(items)),
                                     format_func=lambda index: items[index]["filename"])
                try:
                    st.image(preview_upload(items[index]["data"]), width=500)
                except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError) as error:
                    st.error(f"Cannot preview this image: {error}")
        st.caption("Images are processed locally and kept in this session.")

    with settings_column, st.container(border=True, key="settings"):
        st.subheader("Checklist & OCR")
        required = st.multiselect("Required document types", list(config["required_documents"]),
                                  default=list(config["required_documents"]), format_func=TYPE_NAMES.get)
        bilingual = st.selectbox("OCR language", ["English", "English + Hindi"], key="ocr_language") == "English + Hindi"
        source = st.radio(
            "OCR source", list(OCR_SOURCES), format_func=OCR_SOURCES.get, horizontal=True,
            key="ocr_source",
        )
        st.button("Use phone photo settings", on_click=use_phone_photo_settings,
                  disabled=bilingual and source == "auto",
                  help="Selects English + Hindi and Auto photo. Useful for bilingual certificates and sideways cards.")
        options = processing_controls()
        with st.expander("Required fields"):
            for doc_type in required:
                fields = ", ".join(FIELD_NAMES.get(key, key) for key in config["required_documents"][doc_type])
                st.write(f"**{TYPE_NAMES[doc_type]}** · {fields or 'No required fields'}")

    signature = input_signature(items, options, required, source, config, bilingual=bilingual)
    had_results = "analysis" in st.session_state
    if invalidate_results(st.session_state, signature) and had_results:
        upload_feedback.info("Previous results cleared. Analyze again to update your report.")
    if not required:
        upload_feedback.error("Select at least one required document type.")
    if action.button("Analyze documents", disabled=not items or not required, type="primary", width="stretch"):
        st.session_state.pop("analysis", None)
        try:
            provider = load_real_provider()
        except (ImportError, OSError) as error:
            upload_feedback.error(f"Awaiting real DIP/OCR modules: {error}")
        else:
            try:
                with upload_feedback.container(), st.spinner("Analyzing documents…"):
                    records, views = analyze_uploads(items, options, source, provider, bilingual=bilingual)
                    report = analyze_readiness(records, config, required)
                    st.session_state["analysis"] = {"report": report, "views": views}
                upload_feedback.empty()
            except Exception as error:
                st.session_state.pop("analysis", None)
                upload_feedback.error(f"Analysis could not complete: {error}")
    if "analysis" in st.session_state:
        result = st.session_state["analysis"]
        status = result["report"]["overall_status"]
        upload_feedback.markdown(f"**Analysis complete · {status}.** [View results](#graphia-results)")
        show_results(result)
    st.caption("Project 042 · Sakshi Gupta and Jigisha Baiswar · Readiness reflects the selected demo checklist.")


if __name__ == "__main__":
    main()
