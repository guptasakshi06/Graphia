"""JB04 development-only providers and UI checks. Never real OCR evidence.

The production app never imports this file. AppTest harness explicitly injects
fictional images/text into mocked widget/provider calls, with a visible label.
"""

from io import BytesIO
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
from streamlit.testing.v1 import AppTest

import app
from modules.readiness import analyze_readiness, render_report

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = "FICTIONAL TEST ONLY - NOT REAL OCR\nIncome Certificate\nStudent Name: Asha Example\nCertificate Number: INC-00017"
ORIGINAL = "FICTIONAL TEST ONLY - NOT REAL OCR\nMarksheet\nStudent Name: Bela Example"
OPTIONS = {"denoise": "median", "kernel_size": 3, "contrast": "clahe", "threshold": "otsu",
           "global_threshold": 127, "adaptive_block_size": 31, "adaptive_c": 11.0,
           "morphology": "none", "morph_kernel_size": 2}


class FictionalUpload:
    def __init__(self, name="FICTIONAL_TEST.png", data=None):
        self.name = name
        if data is None:
            buffer = BytesIO()
            Image.new("RGB", (24, 20), (255, 0, 0)).save(buffer, format="PNG")
            data = buffer.getvalue()
        self.data = data

    def getvalue(self):
        return self.data


def fixture_uploads():
    return [FictionalUpload(), FictionalUpload(), FictionalUpload("FICTIONAL_CORRUPT.png", b"broken")]


def fixture_provider():
    """Contract-shaped deterministic fake under tests ONLY, with labeled text."""
    def load(data, max_dimension=1800):
        if data == b"broken":
            raise ValueError("FICTIONAL corrupt image")
        assert max_dimension == 1800
        image = np.zeros((20, 24, 3), dtype=np.uint8)
        image[:, :, 2] = 255
        return image

    def pipeline(image, options=None):
        stages = {name: image.copy() if name == "original" else np.zeros((20, 24), dtype=np.uint8)
                  for name in app.STAGES}
        return {"stages": stages, "ocr_input": stages["morphology"],
                "parameters": {**options, "fixture_only": True}}

    def ocr(image, lang="eng", psm=6, timeout=20):
        return {"text": ORIGINAL if image.ndim == 3 else REFERENCE, "status": "ok",
                "confidence": None, "error": None,
                "engine_config": {"lang": lang, "psm": psm, "timeout": timeout}}
    return load, pipeline, ocr


def harness(missing=False):
    """Executed only by AppTest, never by streamlit run app.py."""
    provider_patch = ('patch("app.load_real_provider", side_effect=ModuleNotFoundError("modules.ocr"))'
                      if missing else 'patch("app.load_real_provider", side_effect=fixture_provider)')
    return f'''
from unittest.mock import patch
import streamlit as st
import app
from test_ui import fixture_uploads, fixture_provider
st.warning("FICTIONAL UI TEST ONLY — NOT REAL OCR OR FINAL EVIDENCE")
with patch("app.st.file_uploader", return_value=fixture_uploads()), {provider_patch}:
    app.main()
'''


class OrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.items = app.collect_uploads(fixture_uploads())
        self.config = json.loads((ROOT / "config/requirements.json").read_text())

    def test_stable_distinct_ids_even_identical_name_and_bytes(self):
        self.assertEqual(self.items, app.collect_uploads(fixture_uploads()))
        self.assertNotEqual(self.items[0]["id"], self.items[1]["id"])
        changed = app.collect_uploads([FictionalUpload(data=b"different")])
        self.assertNotEqual(self.items[0]["id"], changed[0]["id"])

    def test_signature_and_state_invalidation_all_inputs(self):
        signature = app.input_signature(self.items, OPTIONS, ["income_certificate"], "processed", self.config)
        variants = [
            (self.items[:1], OPTIONS, ["income_certificate"], "processed", self.config),
            (self.items, {**OPTIONS, "threshold": "adaptive"}, ["income_certificate"], "processed", self.config),
            (self.items, OPTIONS, ["marksheet"], "processed", self.config),
            (self.items, OPTIONS, ["income_certificate"], "original", self.config),
            (self.items, OPTIONS, ["income_certificate"], "processed", {**self.config, "profile_name": "changed"}),
        ]
        state = {"analysis_signature": signature, "analysis": {"report": "old", "views": "old"}}
        self.assertFalse(app.invalidate_results(state, signature))
        for variant in variants:
            with self.subTest(variant=variant[2:4]):
                state["analysis"] = {"report": "old"}
                new_signature = app.input_signature(*variant)
                self.assertNotEqual(signature, new_signature)
                self.assertTrue(app.invalidate_results(state, new_signature))
                self.assertNotIn("analysis", state)
                state["analysis_signature"] = signature

    def test_selected_ocr_drives_fields_and_duplicate_report(self):
        for source, expected_type, name in [("processed", "income_certificate", "Asha Example"),
                                            ("original", "marksheet", "Bela Example")]:
            with self.subTest(source=source):
                records, views = app.analyze_uploads(self.items, OPTIONS, source, fixture_provider())
                self.assertEqual(records[0]["classification"]["doc_type"], expected_type)
                self.assertEqual(records[0]["fields"]["student_name"], name)
                self.assertEqual(records[0]["ocr"], records[0]["ocr_" + source])
                self.assertEqual(records[2]["ocr"]["status"], "error")
                self.assertEqual(records[2]["classification"]["doc_type"], "unknown")
                self.assertIn("corrupt", views[self.items[2]["id"]]["error"])
                report = analyze_readiness(records, self.config, [expected_type])
                self.assertEqual(report["submitted_file_count"], 3)
                self.assertEqual(report["usable_required_type_count"], 1)
                self.assertEqual(report["readiness_percent"], 100)
                self.assertEqual(report["documents"][0]["filename"], report["documents"][1]["filename"])
                exported = json.loads(json.dumps(report, allow_nan=False))
                self.assertIn("FICTIONAL TEST ONLY", exported["documents"][0]["ocr"]["text"])
                self.assertIn(name, render_report(report))
                self.assertNotIn("stages", exported["documents"][0])
                self.assertEqual(records[0]["processing_parameters"]["resolved_pipeline"],
                                 {**OPTIONS, "fixture_only": True})

    def test_pipeline_failure_keeps_original_available(self):
        load, _, ocr = fixture_provider()
        def broken_pipeline(image, options=None):
            raise ValueError("FICTIONAL pipeline failure")
        for source in ("original", "processed"):
            records, views = app.analyze_uploads(self.items[:1], OPTIONS, source, (load, broken_pipeline, ocr))
            self.assertEqual(records[0]["ocr_original"]["status"], "ok")
            self.assertEqual(records[0]["ocr_processed"]["status"], "error")
            self.assertEqual(records[0]["classification"]["doc_type"], "marksheet" if source == "original" else "unknown")
            self.assertIn("failure", views[self.items[0]["id"]]["error"])

    def test_real_rotated_fictional_identity_image_recovers_name(self):
        manifest = json.loads((ROOT / "dataset/manifest.json").read_text())
        sample = next(row for row in manifest["samples"]
                      if row["doc_type"] == "identity_proof" and row["condition"] == "clear")
        data = BytesIO()
        with Image.open(ROOT / "dataset" / sample["image_path"]) as image:
            image.transpose(Image.Transpose.ROTATE_270).save(data, format="PNG")
        items = app.collect_uploads([FictionalUpload(data=data.getvalue())])
        records, _ = app.analyze_uploads(items, OPTIONS, "auto", app.load_real_provider())
        record = records[0]
        self.assertEqual(record["classification"]["doc_type"], "identity_proof")
        self.assertEqual(record["fields"], sample["expected_fields"])
        self.assertEqual(record["processing_parameters"]["photo_recovery"], "rotated 90° left")

    def test_ocr_exception_and_no_text_keep_all_records(self):
        load, pipeline, _ = fixture_provider()
        def broken_ocr(image, **kwargs):
            raise TimeoutError("FICTIONAL timeout")
        records, _ = app.analyze_uploads(self.items, OPTIONS, "processed", (load, pipeline, broken_ocr))
        self.assertEqual(len(records), 3)
        self.assertTrue(all(record["ocr"]["status"] == "error" for record in records))
        self.assertIn("timeout", records[0]["ocr"]["error"])
        def empty_ocr(image, **kwargs):
            return {"text": "", "status": "no_text", "confidence": None, "error": None,
                    "engine_config": dict(app.ENGINE)}
        records, _ = app.analyze_uploads(self.items[:1], OPTIONS, "processed", (load, pipeline, empty_ocr))
        report = analyze_readiness(records, self.config)
        self.assertEqual(report["readiness_percent"], 0)
        self.assertEqual(report["documents"][0]["ocr"]["status"], "no_text")

    def test_display_bgr_gray_and_preview_normalization(self):
        bgr = np.array([[[0, 0, 255]]], dtype=np.uint8)
        before = bgr.copy()
        np.testing.assert_array_equal(app.display_pixels(bgr), [[[255, 0, 0]]])
        np.testing.assert_array_equal(bgr, before)
        gray = np.array([[7]], dtype=np.uint8)
        np.testing.assert_array_equal(app.display_pixels(gray), gray)
        buffer = BytesIO()
        Image.new("RGBA", (8, 8), (0, 0, 0, 0)).save(buffer, format="PNG")
        self.assertEqual(app.preview_upload(buffer.getvalue()).getpixel((0, 0)), (255, 255, 255))

    def test_production_missing_provider_has_no_fixture_fallback(self):
        import builtins
        real_import = builtins.__import__
        def absent(name, *args, **kwargs):
            if name in ("modules.preprocessing", "modules.ocr"):
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)
        with patch("builtins.__import__", side_effect=absent):
            with self.assertRaises(ModuleNotFoundError):
                app.load_real_provider()
        source = (ROOT / "app.py").read_text()
        self.assertNotIn("from test_ui", source)
        self.assertNotIn("import test_ui", source)
        self.assertNotIn("sys.path", source)


class StreamlitInteractionTests(unittest.TestCase):
    def run_fixture(self, missing=False):
        return AppTest.from_string(harness(missing), default_timeout=15).run()

    def analyze(self, at):
        return at.button[0].click().run()

    def test_production_start_empty_selection_and_no_uploads(self):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()
        self.assertEqual(len(at.exception), 0)
        self.assertTrue(at.button[0].disabled)
        self.assertEqual(at.radio[0].value, "processed")
        at.multiselect[0].set_value([]).run()
        self.assertEqual(len(at.exception), 0)
        self.assertTrue(any("at least one" in error.value for error in at.error))
        self.assertNotIn("analysis", at.session_state)

    def test_missing_modules_clear_message_and_no_downloads(self):
        at = self.analyze(self.run_fixture(missing=True))
        self.assertEqual(len(at.exception), 0)
        self.assertTrue(any("Awaiting real DIP/OCR modules" in error.value for error in at.error))
        self.assertNotIn("analysis", at.session_state)
        self.assertEqual(len(at.get("download_button")), 0)

    def test_download_payloads_match_the_visible_fixture_report(self):
        at = self.run_fixture()
        with patch("app.st.download_button", wraps=app.st.download_button) as downloads:
            self.analyze(at)
        self.assertEqual(len(at.exception), 0)
        report = at.session_state["analysis"]["report"]
        self.assertEqual(downloads.call_count, 2)
        json_call, markdown_call = downloads.call_args_list
        self.assertEqual(json.loads(json_call.args[1]), report)
        self.assertEqual(json_call.kwargs["mime"], "application/json")
        self.assertEqual(json_call.kwargs["file_name"], "readiness_report.json")
        self.assertEqual(markdown_call.args[1], render_report(report))
        self.assertEqual(markdown_call.kwargs["mime"], "text/markdown")
        self.assertIn("FICTIONAL TEST ONLY", markdown_call.args[1])

    def test_retry_failure_clears_previous_report(self):
        at = self.analyze(self.run_fixture())
        self.assertIn("analysis", at.session_state)
        from unittest.mock import Mock
        with patch("test_ui.fixture_provider", new=Mock(side_effect=ModuleNotFoundError("modules.ocr"))):
            self.analyze(at)
        self.assertEqual(len(at.exception), 0)
        self.assertNotIn("analysis", at.session_state)
        self.assertEqual(len(at.get("download_button")), 0)
        self.assertTrue(any("Awaiting real DIP/OCR modules" in error.value for error in at.error))

    def test_fixture_render_downloads_and_all_input_changes_clear_results(self):
        at = self.analyze(self.run_fixture())
        self.assertEqual(len(at.exception), 0)
        report = at.session_state["analysis"]["report"]
        self.assertEqual((report["submitted_file_count"], report["coverage_percent"], report["readiness_percent"]),
                         (3, 25, 25))
        self.assertEqual(len(at.get("download_button")), 2)
        self.assertTrue(any("Asha Example" in element.value for element in at.json))
        self.assertEqual(len(at.get("image")), 14)  # 2 previews + 12 named stages; corrupt stays visible.
        for mutate in (
            lambda ui: ui.selectbox[2].set_value("adaptive"),
            lambda ui: ui.multiselect[0].set_value(["income_certificate"]),
            lambda ui: ui.radio[0].set_value("original"),
        ):
            mutate(at).run()
            self.assertEqual(len(at.exception), 0)
            self.assertNotIn("analysis", at.session_state)
            self.assertEqual(len(at.get("download_button")), 0)
            self.assertTrue(any("Previous results" in info.value for info in at.info))
            self.analyze(at)
            self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.session_state["analysis"]["report"]["documents"][0]["fields"]["student_name"],
                         "Bela Example")
        language = next(widget for widget in at.selectbox if widget.label == "OCR language")
        language.set_value("English + Hindi").run()
        self.assertNotIn("analysis", at.session_state)
        self.assertEqual(len(at.get("download_button")), 0)
        self.analyze(at)
        document = at.session_state["analysis"]["report"]["documents"][0]
        for source in ("original", "processed"):
            self.assertEqual(document["ocr_" + source]["engine_config"], app.BILINGUAL_ENGINE)
        # Different file bytes/count trigger the same production invalidation path.
        with patch("test_ui.fixture_uploads", return_value=[FictionalUpload(data=b"new bytes")]):
            at.run()
        self.assertNotIn("analysis", at.session_state)
        self.assertEqual(len(at.get("download_button")), 0)


if __name__ == "__main__":
    unittest.main()
