"""Known edit counts, reference integrity, error accounting and SG04 artifact audit."""

import contextlib
import csv
import hashlib
from io import StringIO
import json
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
