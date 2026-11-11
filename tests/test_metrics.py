"""Known edit counts, reference integrity, error accounting and SG04 artifact audit."""

import contextlib
import csv
import hashlib
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from modules.preprocessing import load_image
from scripts.run_experiments import (character_error_rate, compare_sg04,
                                     levenshtein_distance, normalize_ocr_text,
                                     run_sg04_experiments, verified_ocr_samples)


ROOT = Path(__file__).resolve().parents[1]


class CERTests(unittest.TestCase):
    def test_known_insert_delete_substitute_and_mixed(self):
        for ref, hyp, distance in (("abc", "abc", 0), ("abc", "abxc", 1),
                                   ("abc", "ac", 1), ("abc", "axc", 1),
                                   ("kitten", "sitting", 3), ("", "abc", 3),
                                   ("abc", "", 3), ("", "", 0)):
            with self.subTest(reference=ref, hypothesis=hyp):
                self.assertEqual(levenshtein_distance(ref, hyp), distance)
                self.assertEqual(levenshtein_distance(hyp, ref), distance)
                if ref:
                    self.assertEqual(character_error_rate(ref, hyp), distance / len(ref))

    def test_normalization_and_punctuation(self):
        self.assertEqual(normalize_ocr_text(" \tStudent NAME:\n Asha  Verma\n"), "student name: asha verma")
        self.assertEqual(character_error_rate("NAME: Asha\nVerma", "name: asha verma"), 0)
        self.assertEqual(normalize_ocr_text("Straße"), "strasse")
        self.assertEqual(character_error_rate("A-B", "AB"), 1 / 3)

    def test_empty_reference_undefined_and_cer_over_one(self):
        for ref, hyp in (("", ""), (" \n", "abc")):
            with self.assertRaisesRegex(ValueError, "nonempty"):
                character_error_rate(ref, hyp)
        self.assertEqual(character_error_rate("a", "abcd"), 3)
        self.assertEqual(character_error_rate("abc", ""), 1)

    def test_invalid_text_rejected(self):
        for value in (None, 3, b"abc"):
            with self.assertRaises(ValueError):
                character_error_rate("abc", value)
            with self.assertRaises(ValueError):
                levenshtein_distance(value, "abc")

    def test_reference_hash_and_review_checks(self):
        manifest_path = ROOT / "dataset/manifest.json"
        _, _, samples = verified_ocr_samples(manifest_path)
        self.assertEqual(len(samples), 8)
        # Supply changed metadata through the file reader; no dataset edits.
        original_read = Path.read_text

        def changed_read(path, *args, **kwargs):
            value = original_read(path, *args, **kwargs)
            if path == manifest_path:
                manifest = json.loads(value)
                manifest["samples"][0]["reference_sha256"] = "0" * 64
                return json.dumps(manifest)
            return value

        with patch.object(Path, "read_text", changed_read), self.assertRaisesRegex(ValueError, "hash mismatch"):
            verified_ocr_samples(manifest_path)

    def test_error_saved_with_null_metrics_and_nonzero_cli_signal(self):
        manifest_path = ROOT / "dataset/manifest.json"
        manifest, review, samples = verified_ocr_samples(manifest_path)
        failed = {"text": "", "status": "error", "confidence": None, "error": "test-only timeout",
                  "engine_config": {"lang": "eng", "psm": 6, "timeout": 20}}
        with tempfile.TemporaryDirectory() as folder:
            with patch("scripts.run_experiments.verified_ocr_samples", return_value=(manifest, review, samples[:1])), \
                    patch("scripts.run_experiments.extract_text", return_value=failed), \
                    patch("pytesseract.get_tesseract_version", side_effect=OSError("test-only missing executable")), \
                    contextlib.redirect_stdout(StringIO()), self.assertRaisesRegex(ValueError, "incomplete"):
                run_sg04_experiments(manifest_path, folder)
            report = json.loads((Path(folder) / "metrics.json").read_text())
            self.assertIsNone(report["versions"]["tesseract"])
            self.assertIn("missing executable", report["engine_version_error"])
            self.assertEqual(len(report["rows"]), 4)
            for row in report["rows"]:
                self.assertIsNone(row["cer"])
                self.assertIsNone(row["edit_distance"])
            for method in report["summary"].values():
                self.assertEqual(method["error_count"], 1)
                self.assertIsNone(method["mean_cer"])


class SavedOCRAuditTests(unittest.TestCase):
    def test_actual_saved_ocr_images_raw_text_cer_and_summary(self):
        folder = ROOT / "outputs/experiments/SG04"
        report = json.loads((folder / "metrics.json").read_text())
        manifest_path = ROOT / "dataset/manifest.json"
        _, review, samples = verified_ocr_samples(manifest_path)
        self.assertEqual(report["manifest_sha256"], hashlib.sha256(manifest_path.read_bytes()).hexdigest())
        self.assertEqual(report["visual_review_sha256"], hashlib.sha256(review.read_bytes()).hexdigest())
        self.assertEqual(len(report["rows"]), 32)
        self.assertEqual(len({(r["sample_id"], r["method"]) for r in report["rows"]}), 32)
        for sample, reference in samples:
            image = load_image(manifest_path.parent / sample["image_path"])
            before = image.copy()
            alternatives = compare_sg04(image)
            np.testing.assert_array_equal(image, before)
            normalized_ref = normalize_ocr_text(reference)
            self.assertEqual((folder / sample["id"] / "reference_normalized.txt").read_text(), normalized_ref + "\n")
            for row in (r for r in report["rows"] if r["sample_id"] == sample["id"]):
                raw_path = folder / row["raw_text_path"]
                self.assertEqual(raw_path.read_text(), row["ocr"]["text"])
                self.assertEqual(hashlib.sha256(raw_path.read_bytes()).hexdigest(), row["raw_text_sha256"])
                self.assertEqual(row["ocr"]["status"], "ok")
                self.assertIsNone(row["ocr"]["error"])
                self.assertIsNone(row["ocr"]["confidence"])
                self.assertEqual(row["ocr"]["engine_config"], {"lang": "eng", "psm": 6, "timeout": 20.0})
                self.assertEqual(row["normalized_reference"], normalized_ref)
                self.assertEqual(row["normalized_hypothesis"], normalize_ocr_text(row["ocr"]["text"]))
                self.assertEqual(row["edit_distance"], levenshtein_distance(normalized_ref, row["normalized_hypothesis"]))
                self.assertEqual(row["cer"], character_error_rate(reference, row["ocr"]["text"]))
                self.assertEqual(row["parameters"], alternatives[row["method"]][1])
                image_path = (manifest_path.parent if row["ocr_image_base"] == "dataset" else folder) / row["ocr_image"]
                self.assertEqual(hashlib.sha256(image_path.read_bytes()).hexdigest(), row["ocr_image_sha256"])
                flags = cv2.IMREAD_COLOR if row["method"] == "original" else cv2.IMREAD_GRAYSCALE
                np.testing.assert_array_equal(cv2.imread(str(image_path), flags), alternatives[row["method"]][0])
        with (folder / "metrics.csv").open(newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
        self.assertEqual(len(csv_rows), 32)
        for table, row in zip(csv_rows, report["rows"]):
            self.assertEqual(float(table["cer"]), row["cer"])
            self.assertEqual(int(table["edit_distance"]), row["edit_distance"])
        for method, values in report["summary"].items():
            selected = [r for r in report["rows"] if r["method"] == method]
            self.assertEqual(values["scored_count"], 8)
            self.assertEqual(values["error_count"], 0)
            self.assertEqual(values["total_edits"], sum(r["edit_distance"] for r in selected))
            self.assertEqual(values["mean_cer"], sum(r["cer"] for r in selected) / 8)
            self.assertEqual(values["pooled_cer"], sum(r["edit_distance"] for r in selected) / sum(r["reference_characters"] for r in selected))


class FinalEvaluationTests(unittest.TestCase):
    """Final evidence checks use measured text; no fake OCR enters the app."""

    def test_no_text_and_engine_failure_have_different_denominators(self):
        from scripts.evaluate_dataset import evaluate_observation, summarize
        _, _, samples = verified_ocr_samples(ROOT / "dataset/manifest.json")
        sample, reference = samples[0]
        rows = []
        for status in ("no_text", "error"):
            result = {"text": "", "status": status, "confidence": None,
                      "error": "test-only timeout" if status == "error" else None,
                      "engine_config": {"lang": "eng", "psm": 6, "timeout": 20}}
            row = evaluate_observation(sample, reference, result)
            self.assertFalse(row["type_correct"])
            self.assertEqual(row["present_field_correct"], 0)
            self.assertTrue(row["reference_diagnostic"]["rules_pass"])
            self.assertEqual(row["failure_attribution"], "ocr_no_text" if status == "no_text" else "ocr_engine_error")
            self.assertEqual(row["cer"], 1 if status == "no_text" else None)
            rows.append({**row, "method": "test-only", "ocr": result})
        totals = summarize(rows)["test-only"]
        self.assertEqual(totals["scored_count"], 1)
        self.assertEqual(totals["error_count"], 1)
        self.assertEqual(totals["no_text_count"], 1)
        self.assertEqual(totals["type_denominator"], 2)
        self.assertEqual(totals["pooled_cer"], 1)

    def test_field_loss_can_exist_when_type_and_normalized_cer_pass(self):
        from scripts.evaluate_dataset import evaluate_observation
        _, _, samples = verified_ocr_samples(ROOT / "dataset/manifest.json")
        sample, reference = samples[0]
        # Losing a label's line boundary is hidden by CER whitespace normalization,
        # but the conservative extractor correctly refuses the combined line.
        damaged = reference.replace("Student Name: Asha Verma\n", "Student Name: Asha Verma ")
        result = {"text": damaged, "status": "ok", "confidence": None,
                  "error": None, "engine_config": {"lang": "eng", "psm": 6, "timeout": 20}}
        row = evaluate_observation(sample, reference, result)
        self.assertEqual(row["cer"], 0)
        self.assertTrue(row["type_correct"])
        self.assertLess(row["present_field_correct"], row["present_field_count"])
        self.assertEqual(row["failure_attribution"], "ocr_path_mismatch_reference_rules_pass")
        self.assertTrue(row["reference_diagnostic"]["rules_pass"])

    @unittest.skipUnless((ROOT / ".git").exists(), "frozen source verification requires Git history")
    def test_final_measured_sources_match_frozen_commit(self):
        from scripts.evaluate_dataset import SOURCE_FILES
        folder = ROOT / "outputs/experiments/SG05"
        report = json.loads((folder / "metrics.json").read_text())
        freeze = json.loads((ROOT / "docs/merge/M02-freeze.json").read_text())
        commit = freeze["merged_evidence_commit"]
        for relative in SOURCE_FILES:
            source = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)
            self.assertEqual(hashlib.sha256(source).hexdigest(), report["source_sha256"][relative], relative)

    def test_final_artifact_integrity_and_comparison_coverage(self):
        from scripts.evaluate_dataset import COMPARISONS
        from PIL import Image
        folder = ROOT / "outputs/experiments/SG05"
        report = json.loads((folder / "metrics.json").read_text())
        hashes = json.loads((folder / "artifact_sha256.json").read_text())
        actual_files = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}
        self.assertEqual(set(hashes), actual_files - {"artifact_sha256.json"})
        for relative, digest in hashes.items():
            self.assertEqual(hashlib.sha256((folder / relative).read_bytes()).hexdigest(), digest, relative)
            if relative.endswith(".png"):
                with Image.open(folder / relative) as im:
                    im.verify()
        self.assertEqual(report["comparison_groups"], COMPARISONS)
        self.assertEqual(len(COMPARISONS), 7)
        self.assertEqual(report["sample_count"], 8)
        self.assertEqual(report["independent_layout_count"], 4)
        self.assertEqual(report["method_ocr_calls"], 112)
        self.assertEqual(report["production_orchestrator_ocr_calls"], 16)
        self.assertEqual(len(report["rows"]), 112)
        self.assertEqual(len({(r["sample_id"], r["method"]) for r in report["rows"]}), 112)
        for sample_id in {r["sample_id"] for r in report["rows"]}:
            for figure in report["comparison_figures_per_sample"].values():
                self.assertTrue((folder / sample_id / figure).is_file())

    def test_final_saved_pixels_text_measurements_and_rule_outcomes(self):
        from modules.classification import classify_document
        from modules.extraction import extract_fields
        from modules.preprocessing import to_grayscale
        from scripts.evaluate_dataset import final_methods
        folder = ROOT / "outputs/experiments/SG05"
        report = json.loads((folder / "metrics.json").read_text())
        _, _, samples = verified_ocr_samples(ROOT / "dataset/manifest.json")
        for sample, reference in samples:
            original = load_image(ROOT / "dataset" / sample["image_path"])
            before = original.copy()
            alternatives, _ = final_methods(original)
            np.testing.assert_array_equal(before, original)
            self.assertEqual((folder / sample["id"] / "reference_raw.txt").read_text(), reference)
            self.assertEqual((folder / sample["id"] / "reference_normalized.txt").read_text(), normalize_ocr_text(reference) + "\n")
            selected = [r for r in report["rows"] if r["sample_id"] == sample["id"]]
            self.assertEqual(set(r["method"] for r in selected), set(alternatives))
            for row in selected:
                image, settings = alternatives[row["method"]]
                base = ROOT / "dataset" if row["ocr_image_base"] == "dataset" else folder
                image_path = base / row["ocr_image"]
                flag = cv2.IMREAD_COLOR if image.ndim == 3 else cv2.IMREAD_GRAYSCALE
                np.testing.assert_array_equal(cv2.imread(str(image_path), flag), image)
                self.assertEqual(row["ocr_image_sha256"], hashlib.sha256(image_path.read_bytes()).hexdigest())
                self.assertEqual(row["parameters"], settings)
                self.assertEqual(row["shape"], list(image.shape))
                self.assertEqual(row["dtype"], "uint8")
                gray = to_grayscale(image) if image.ndim == 3 else image
                self.assertEqual(row["grayscale_stddev"], float(np.std(gray, dtype=np.float64)))
                self.assertEqual(row["histogram_counts"], np.bincount(gray.ravel(), minlength=256).tolist())
                self.assertEqual(row["dark_pixel_count_lt128"], int(np.count_nonzero(gray < 128)))
                self.assertEqual(row["ocr"]["text"], (folder / row["raw_text_path"]).read_text())
                self.assertEqual(row["normalized_hypothesis"], normalize_ocr_text(row["ocr"]["text"]))
                self.assertEqual(row["normalized_reference"], normalize_ocr_text(reference))
                if row["ocr"]["status"] == "error":
                    self.assertIsNone(row["cer"])
                else:
                    self.assertEqual(row["cer"], character_error_rate(reference, row["ocr"]["text"]))
                self.assertEqual(row["classification"], classify_document(row["ocr"]["text"]))
                self.assertEqual(row["fields"], extract_fields(row["ocr"]["text"], row["classification"]["doc_type"]))
                self.assertEqual(row["expected_fields"], sample["expected_fields"])
                self.assertEqual(row["present_field_correct"], sum(v is not None and v == row["fields"][k]
                                 for k, v in sample["expected_fields"].items()))

    def test_final_summaries_csv_and_paired_comparisons(self):
        folder = ROOT / "outputs/experiments/SG05"
        report = json.loads((folder / "metrics.json").read_text())
        for method, summary in report["summary"].items():
            rows = [r for r in report["rows"] if r["method"] == method]
            scored = [r for r in rows if r["cer"] is not None]
            self.assertEqual(summary["sample_count"], 8)
            self.assertEqual(summary["type_correct"], sum(r["classification"]["doc_type"] == r["expected_type"] for r in rows))
            self.assertEqual(summary["present_field_count"], 28)
            self.assertEqual(summary["absent_field_count"], 4)
            self.assertEqual(summary["present_field_correct"], sum(r["present_field_correct"] for r in rows))
            self.assertEqual(summary["total_edits"], sum(r["edit_distance"] for r in scored))
            self.assertEqual(summary["total_reference_characters"], sum(r["reference_characters"] for r in scored))
            self.assertEqual(summary["pooled_cer"], summary["total_edits"] / summary["total_reference_characters"])
        with (folder / "metrics.csv").open(newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
        self.assertEqual(len(csv_rows), 112)
        for table, row in zip(csv_rows, report["rows"]):
            self.assertEqual(table["sample_id"], row["sample_id"])
            self.assertEqual(table["method"], row["method"])
            self.assertEqual(float(table["cer"]), row["cer"])
            self.assertEqual(json.loads(table["fields"]), row["fields"])
            self.assertEqual(json.loads(table["parameters"]), row["parameters"])
        with (folder / "original_processed.csv").open(newline="") as handle:
            pairs = list(csv.DictReader(handle))
        self.assertEqual(len(pairs), 8)
        for pair in pairs:
            matches = {r["method"]: r for r in report["rows"] if r["sample_id"] == pair["sample_id"]}
            self.assertEqual(float(pair["original_cer"]), matches["original"]["cer"])
            self.assertEqual(float(pair["processed_cer"]), matches["pipeline_default"]["cer"])

    def test_real_integrated_results_stages_and_readiness(self):
        from modules.readiness import analyze_readiness, render_report
        from modules.preprocessing import run_pipeline
        folder = ROOT / "outputs/experiments/SG05"
        report = json.loads((folder / "integrated_report.json").read_text())
        observations = json.loads((folder / "integrated_observations.json").read_text())
        method_report = json.loads((folder / "metrics.json").read_text())
        config = json.loads((ROOT / "config/requirements.json").read_text())
        self.assertEqual(report, analyze_readiness(report["documents"], config))
        self.assertEqual((folder / "integrated_report.md").read_text(), render_report(report))
        self.assertEqual(report["submitted_file_count"], 8)
        self.assertEqual(report["detected_required_type_count"], 4)
        self.assertEqual(report["usable_required_type_count"], 4)
        self.assertEqual(report["overall_status"], "Ready")
        _, _, samples = verified_ocr_samples(ROOT / "dataset/manifest.json")
        self.assertEqual(len(observations), len(samples))
        for (sample, _), record, obs in zip(samples, report["documents"], observations):
            self.assertEqual(record["classification"]["doc_type"], sample["doc_type"])
            self.assertEqual(record["fields"], sample["expected_fields"])
            self.assertEqual(obs["sample_id"], sample["id"])
            self.assertIsNone(obs["view_error"])
            self.assertTrue(obs["type_correct"])
            stages = run_pipeline(load_image(ROOT / "dataset" / sample["image_path"]))["stages"]
            self.assertEqual(set(obs["stages"]), set(stages))
            for name, pixels in stages.items():
                self.assertEqual(obs["stages"][name]["array_sha256"], hashlib.sha256(pixels.tobytes()).hexdigest())
            for key, method in (("ocr_original", "original"), ("ocr_processed", "pipeline_default")):
                row = next(r for r in method_report["rows"] if r["sample_id"] == sample["id"] and r["method"] == method)
                self.assertEqual(record[key], row["ocr"])
                self.assertEqual(obs[key], row["ocr"])
        for filename in ("readiness_by_method.json", "readiness_submissions.json"):
            for readiness in json.loads((folder / filename).read_text()).values():
                self.assertEqual(readiness, analyze_readiness(readiness["documents"], config))


if __name__ == "__main__":
    unittest.main()
