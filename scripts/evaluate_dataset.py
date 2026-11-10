"""SG05 final local evaluation; fictional manifest only, never private uploads.

Run with .venv/bin/python scripts/evaluate_dataset.py. Outputs are deterministic
for the same source/software and must go into an empty directory. No settings
are tuned using reference text. The production application is imported unchanged.
"""

import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import cv2
import matplotlib
import numpy as np
import pytesseract

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402
from modules.classification import classify_document  # noqa: E402
from modules.extraction import extract_fields  # noqa: E402
from modules.ocr import extract_text  # noqa: E402
from modules.preprocessing import load_image, to_grayscale  # noqa: E402
from modules.readiness import analyze_readiness, render_report  # noqa: E402
from scripts.run_experiments import (  # noqa: E402
    CER_NORMALIZATION, compare_methods, compare_sg03, levenshtein_distance,
    normalize_ocr_text, plt, save_comparison, save_histograms, save_sg03_comparison,
    verified_ocr_samples,
)

# Frozen code baseline, rather than the current documentation/evidence commit.
# This remains reproducible after the containing SG05 commit is created.
M01_BASELINE = "183ff6bfa6e67e2156eafc282044eb151e07ad39"

COMPARISONS = {
    "1_original_grayscale": ["original", "grayscale"],
    "2_contrast": ["original", "equalized", "clahe"],
    "3_filters": ["grayscale", "gaussian", "median"],
    "4_thresholds": ["grayscale", "global", "otsu", "adaptive"],
    "5_erosion_dilation": ["otsu", "erosion", "dilation"],
    "6_opening_closing": ["otsu", "opening", "closing"],
    "7_original_processed_ocr": ["original", "pipeline_default"],
}
FIGURES = {
    "1_original_grayscale": "early.png", "2_contrast": "early.png",
    "3_filters": "early.png", "4_thresholds": "thresholds.png",
    "5_erosion_dilation": "morphology.png", "6_opening_closing": "morphology.png",
    "7_original_processed_ocr": "ocr_comparison.png",
}
SOURCE_FILES = [
    "app.py", "config/requirements.json", "TEAM_CONTRACT.md",
    "modules/preprocessing.py", "modules/ocr.py", "modules/classification.py",
    "modules/extraction.py", "modules/readiness.py", "scripts/run_experiments.py",
    "scripts/evaluate_dataset.py",
]


def file_hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def save_csv(path, rows, columns):
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row[key], sort_keys=True)
                             if isinstance(row[key], (dict, list)) else row[key]
                             for key in columns})


def final_methods(image):
    """Fourteen fixed alternatives; competing methods share the same input."""
    alternatives = compare_methods(image)
    later, pipeline = compare_sg03(image)
    alternatives.update({name: value for name, value in later.items() if name != "grayscale"})
    return alternatives, pipeline


def save_ocr_pair(alternatives, destination, title):
    """Show the original and fixed processed page with no unused panels."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
    for ax, method in zip(axes, ("original", "pipeline_default")):
        image = alternatives[method][0]
        if image.ndim == 3:
            ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), interpolation="nearest")
        else:
            ax.imshow(image, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        ax.set_title(method)
        ax.axis("off")
    fig.suptitle(title)
    fig.savefig(destination, dpi=120)
    plt.close(fig)


def evaluate_observation(sample, reference, result):
    """Compare real OCR rules to expected values and reference-only diagnostics.

    The reference path diagnoses rules; its output is never used as OCR output.
    Exact field scoring is deliberately stricter than case/space-normalized CER.
    Missing optional certificate numbers are counted separately from present fields.
    """
    expected_type, expected = sample["doc_type"], sample["expected_fields"]
    classification = classify_document(result["text"])
    fields = extract_fields(result["text"], classification["doc_type"])
    ref_class = classify_document(reference)
    ref_fields = extract_fields(reference, expected_type)
    oracle_fields = extract_fields(result["text"], expected_type)
    differences = []
    if classification["doc_type"] != expected_type:
        differences.append({"item": "doc_type", "expected": expected_type,
                            "observed": classification["doc_type"]})
    for field, value in expected.items():
        if fields[field] != value:
            differences.append({"item": field, "expected": value, "observed": fields[field]})
    reference_rules_pass = ref_class["doc_type"] == expected_type and ref_fields == expected
    attribution = "none"
    if result["status"] == "error":
        attribution = "ocr_engine_error"
    elif result["status"] == "no_text":
        attribution = "ocr_no_text"
    elif differences:
        attribution = ("ocr_path_mismatch_reference_rules_pass" if reference_rules_pass
                       else "reference_rule_mismatch_needs_review")
    normalized_ref = normalize_ocr_text(reference)
    normalized_hyp = normalize_ocr_text(result["text"])
    edits = None if result["status"] == "error" else levenshtein_distance(normalized_ref, normalized_hyp)
    if attribution == "none" and edits:
        attribution = "ocr_text_difference_observed_rules_pass"
    return {
        "expected_type": expected_type, "classification": classification,
        "type_correct": classification["doc_type"] == expected_type,
        "expected_fields": expected, "fields": fields,
        "present_field_count": sum(value is not None for value in expected.values()),
        "present_field_correct": sum(value is not None and fields[key] == value for key, value in expected.items()),
        "absent_field_count": sum(value is None for value in expected.values()),
        "absent_field_correct": sum(value is None and fields[key] is None for key, value in expected.items()),
        "differences": differences, "failure_attribution": attribution,
        "reference_diagnostic": {"purpose": "rule diagnostic only; not OCR evidence",
                                 "classification": ref_class, "fields": ref_fields,
                                 "rules_pass": reference_rules_pass},
        "fields_with_expected_type_diagnostic": oracle_fields,
        "normalized_reference": normalized_ref, "normalized_hypothesis": normalized_hyp,
        "reference_characters": len(normalized_ref), "edit_distance": edits,
        "cer": edits / len(normalized_ref) if edits is not None else None,
    }


def summarize(rows):
    """Report denominators explicitly; error rows are unscored, no_text is scored."""
    summaries = {}
    for method in dict.fromkeys(row["method"] for row in rows):
        selected = [row for row in rows if row["method"] == method]
        scored = [row for row in selected if row["cer"] is not None]
        total_chars = sum(row["reference_characters"] for row in scored)
        summaries[method] = {
            "sample_count": len(selected), "scored_count": len(scored),
            "error_count": sum(row["ocr"]["status"] == "error" for row in selected),
            "no_text_count": sum(row["ocr"]["status"] == "no_text" for row in selected),
            "total_edits": sum(row["edit_distance"] for row in scored),
            "total_reference_characters": total_chars,
            "pooled_cer": sum(row["edit_distance"] for row in scored) / total_chars if total_chars else None,
            "mean_cer": sum(row["cer"] for row in scored) / len(scored) if scored else None,
            "type_correct": sum(row["type_correct"] for row in selected),
            "type_denominator": len(selected),
            **{key: sum(row[key] for row in selected) for key in (
                "present_field_count", "present_field_correct", "absent_field_count", "absent_field_correct")},
        }
    return summaries


def record_for_method(sample_id, method, result, original_result, observation, parameters):
    """Development evaluation record using actual OCR from a fixed alternative."""
    return {
        "id": sample_id, "filename": sample_id + ".png",
        "ocr_source": "original" if method == "original" else "processed",
        "ocr": result, "ocr_original": original_result, "ocr_processed": result,
        "classification": observation["classification"], "fields": observation["fields"],
        "processing_parameters": {"evaluation_method": method, "resolved": parameters},
    }


def run_evaluation(manifest_path, output_dir):
    manifest_path, output_dir = Path(manifest_path), Path(output_dir)
    manifest, review_path, samples = verified_ocr_samples(manifest_path)
    subprocess.run(["git", "merge-base", "--is-ancestor", M01_BASELINE, "HEAD"],
                   cwd=ROOT, check=True)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Output directory must be empty to prevent stale evidence or overwrites.")
    output_dir.mkdir(parents=True, exist_ok=True)
    config = json.loads((ROOT / "config/requirements.json").read_text())
    rows, method_records = [], {}
    for sample, reference in samples:
        sample_dir = output_dir / sample["id"]
        sample_dir.mkdir()
        (sample_dir / "reference_raw.txt").write_text(reference, encoding="utf-8")
        (sample_dir / "reference_normalized.txt").write_text(normalize_ocr_text(reference) + "\n", encoding="utf-8")
        original = load_image(manifest_path.parent / sample["image_path"])
        before = original.copy()
        alternatives, _ = final_methods(original)
        early = {name: alternatives[name] for name in compare_methods(original)}
        save_comparison(early, sample_dir / "early.png", sample["id"] + " | independent alternatives")
        save_histograms(early, sample_dir / "histograms.png", sample["id"])
        save_sg03_comparison(alternatives, COMPARISONS["4_thresholds"], sample_dir / "thresholds.png", sample["id"])
        save_sg03_comparison(alternatives, ["otsu", "erosion", "dilation", "opening", "closing"],
                              sample_dir / "morphology.png", sample["id"] + " | white-text operations, restored polarity")
        save_ocr_pair(alternatives, sample_dir / "ocr_comparison.png", sample["id"] + " | fixed contract default")
        original_result = None
        for method, (image, parameters) in alternatives.items():
            result = extract_text(image, **app.ENGINE)
            if method == "original":
                original_result = result
            observation = evaluate_observation(sample, reference, result)
            text_path = Path(sample["id"]) / f"{method}.txt"
            (output_dir / text_path).write_text(result["text"], encoding="utf-8")
            image_path = Path(sample["image_path"]) if method == "original" else Path(sample["id"]) / f"{method}.png"
            if method != "original" and not cv2.imwrite(str(output_dir / image_path), image):
                raise OSError(f"Could not save {image_path}")
            gray = to_grayscale(image) if image.ndim == 3 else image
            record = record_for_method(sample["id"], method, result, original_result, observation, parameters)
            readiness = analyze_readiness([record], config)
            method_records.setdefault(method, []).append(record)
            row = {
                "sample_id": sample["id"], "condition": sample["condition"], "method": method,
                "source_image": sample["image_path"], "source_sha256": sample["image_sha256"],
                "reference_path": sample["reference_path"], "reference_sha256": sample["reference_sha256"],
                "parameters": parameters, "shape": list(image.shape), "dtype": str(image.dtype),
                "grayscale_stddev": float(np.std(gray, dtype=np.float64, ddof=0)),
                "grayscale_mean": float(np.mean(gray, dtype=np.float64)),
                "histogram_counts": np.bincount(gray.ravel(), minlength=256).tolist(),
                "dark_pixel_count_lt128": int(np.count_nonzero(gray < 128)),
                "ocr_image": image_path.as_posix(),
                "ocr_image_base": "dataset" if method == "original" else "output_dir",
                "ocr_image_sha256": file_hash((manifest_path.parent if method == "original" else output_dir) / image_path),
                "raw_text_path": text_path.as_posix(), "raw_text_sha256": file_hash(output_dir / text_path),
                "ocr": result, **observation, "readable": readiness["documents"][0]["readable"],
                "usable": readiness["documents"][0]["usable"],
                "missing_required_fields": readiness["documents"][0]["missing_required_fields"],
                "readiness_problems": readiness["documents"][0]["problems"],
            }
            rows.append(row)
            print(f"SG05 {sample['id']} / {method}: {result['status']}, CER={row['cer']}, "
                  f"type={row['classification']['doc_type']}, fields={row['present_field_correct']}/{row['present_field_count']}", flush=True)
        np.testing.assert_array_equal(original, before)

    # Exercise the unchanged production upload orchestrator, including bytes loader,
    # original and processed real engine calls. This is separate from method trials.
    items = [{"id": sample["id"], "filename": Path(sample["image_path"]).name,
              "data": (manifest_path.parent / sample["image_path"]).read_bytes()} for sample, _ in samples]
    records, views = app.analyze_uploads(items, {}, "processed", app.load_real_provider())
    integrated = analyze_readiness(records, config)
    save_json(output_dir / "integrated_report.json", integrated)
    (output_dir / "integrated_report.md").write_text(render_report(integrated), encoding="utf-8")
    integrated_rows = []
    for (sample, reference), record in zip(samples, records):
        view = views[record["id"]]
        integrated_rows.append({
            "sample_id": sample["id"], "ocr": record["ocr"],
            **evaluate_observation(sample, reference, record["ocr"]),
            "ocr_original": record["ocr_original"], "ocr_processed": record["ocr_processed"],
            "view_error": view["error"],
            "stages": {name: {"shape": list(image.shape), "dtype": str(image.dtype),
                               "array_sha256": sha256(image.tobytes()).hexdigest()}
                       for name, image in view["stages"].items()},
        })
    save_json(output_dir / "integrated_observations.json", integrated_rows)
    # Checklist calculations from measured records, no new OCR, include duplicates.
    readiness_by_method = {method: analyze_readiness(records, config)
                           for method, records in method_records.items()}
    save_json(output_dir / "readiness_by_method.json", readiness_by_method)
    scenarios = {}
    for name, indices in {"all_eight": list(range(len(samples))),
                          "clear_only": [i for i, (s, _) in enumerate(samples) if s["condition"] == "clear"],
                          "degraded_only": [i for i, (s, _) in enumerate(samples) if s["condition"] != "clear"]}.items():
        scenarios[name] = analyze_readiness([records[i] for i in indices], config)
    save_json(output_dir / "readiness_submissions.json", scenarios)
    version, version_error = None, None
    try:
        version = str(pytesseract.get_tesseract_version())
    except (OSError, RuntimeError) as exc:
        version_error = str(exc)
    report = {
        "sprint": "SG05", "purpose": "Final measured candidates from M01 code; M02 freeze still required",
        "baseline_commit": M01_BASELINE,
        "source_sha256": {path: file_hash(ROOT / path) for path in SOURCE_FILES},
        "manifest_sha256": file_hash(manifest_path), "visual_review_sha256": file_hash(review_path),
        "ground_truth": "SG01 assistant visual review with matching hashes; no student/human review claimed",
        "versions": {"python": sys.version.split()[0], "tesseract": version,
                     "pytesseract": pytesseract.__version__, "opencv": cv2.__version__,
                     "numpy": np.__version__, "matplotlib": matplotlib.__version__},
        "engine_version_error": version_error, "ocr_config": app.ENGINE,
        "normalization": CER_NORMALIZATION, "empty_reference": "Rejected before OCR",
        "contrast_definition": "Population grayscale standard deviation ddof=0; not OCR accuracy",
        "comparison_groups": COMPARISONS, "comparison_figures_per_sample": FIGURES,
        "loader_max_dimension": 1800, "morphology_input": "grayscale Otsu; white text foreground restored after operation",
        "field_scoring": "Exact case-sensitive strings; 28 present and 4 absent slots per method on all eight samples",
        "failure_attribution": "Reference and expected-type diagnostics separate input corruption from rule limitations; not a causal proof",
        "selected_default": "Unchanged contract-v1 median3 -> CLAHE2.0/8x8 -> Otsu -> no morphology; processed OCR",
        "sample_count": len(samples), "independent_layout_count": sum(s["derivative_of"] is None for s, _ in samples),
        "method_ocr_calls": len(rows), "production_orchestrator_ocr_calls": 2 * len(records),
        "rows": rows, "summary": summarize(rows),
    }
    save_json(output_dir / "metrics.json", report)
    flat_rows = [{**row, "status": row["ocr"]["status"], "error": row["ocr"]["error"],
                  "engine_config": row["ocr"]["engine_config"],
                  "observed_type": row["classification"]["doc_type"]} for row in rows]
    columns = ["sample_id", "condition", "method", "parameters", "engine_config", "status", "error",
               "grayscale_stddev", "reference_characters", "edit_distance", "cer", "expected_type",
               "observed_type", "type_correct", "expected_fields", "fields", "present_field_correct",
               "present_field_count", "absent_field_correct", "absent_field_count", "readable", "usable",
               "missing_required_fields", "failure_attribution", "differences", "raw_text_path"]
    save_csv(output_dir / "metrics.csv", flat_rows, columns)
    save_csv(output_dir / "summary.csv", [{"method": method, **values} for method, values in report["summary"].items()],
             ["method", *next(iter(report["summary"].values()))])
    # Explicit paired original/default table makes the required OCR comparison easy to reuse.
    paired = []
    for sample, _ in samples:
        matches = {r["method"]: r for r in rows if r["sample_id"] == sample["id"]}
        paired.append({"sample_id": sample["id"], "condition": sample["condition"],
                       "original_cer": matches["original"]["cer"],
                       "processed_cer": matches["pipeline_default"]["cer"],
                       "original_contrast": matches["original"]["grayscale_stddev"],
                       "processed_contrast": matches["pipeline_default"]["grayscale_stddev"],
                       "original_parameters": matches["original"]["parameters"],
                       "processed_parameters": matches["pipeline_default"]["parameters"]})
    save_csv(output_dir / "original_processed.csv", paired, list(paired[0]))
    save_json(output_dir / "artifact_sha256.json", {
        path.relative_to(output_dir).as_posix(): file_hash(path)
        for path in sorted(output_dir.rglob("*")) if path.is_file()})
    if any(row["ocr"]["status"] == "error" for row in rows) or any(
        r[key]["status"] == "error" for r in records for key in ("ocr_original", "ocr_processed")
    ) or any(view["error"] for view in views.values()):
        raise ValueError("Engine/pipeline failures saved; SG05 evaluation incomplete.")
    print(f"SG05 saved {len(rows)} method rows + {len(records)} production records to {output_dir}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "dataset/manifest.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/experiments/SG05")
    args = parser.parse_args()
    try:
        run_evaluation(args.manifest, args.output_dir)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Evaluation error: {exc}\n")


if __name__ == "__main__":
    main()
