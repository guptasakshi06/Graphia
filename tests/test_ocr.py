"""Contract/error checks plus explicitly real Tesseract acceptance checks."""

import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pytesseract

from modules.ocr import extract_text
from modules.preprocessing import load_image


ROOT = Path(__file__).resolve().parents[1]


class OCRContractTests(unittest.TestCase):
    def setUp(self):
        self.gray = np.full((80, 160), 255, dtype=np.uint8)

    def test_raw_text_exact_result_and_settings(self):
        with patch("modules.ocr.pytesseract.image_to_string", return_value="  AbC\n42\n") as engine:
            result = extract_text(self.gray)
        self.assertEqual(result, {"text": "  AbC\n42\n", "status": "ok", "confidence": None,
                                  "error": None, "engine_config": {"lang": "eng", "psm": 6, "timeout": 20.0}})
        self.assertEqual(engine.call_args.kwargs, {"lang": "eng", "config": "--psm 6", "timeout": 20.0})
        json.dumps(result, allow_nan=False)

    def test_bgr_to_rgb_and_input_preserved(self):
        bgr = np.array([[[10, 20, 30], [40, 50, 60]]], dtype=np.uint8)
        before = bgr.copy()

        def engine(image, **kwargs):
            np.testing.assert_array_equal(image, before[..., ::-1])
            image[:] = 0
            return "Color 042"

        with patch("modules.ocr.pytesseract.image_to_string", side_effect=engine):
            self.assertEqual(extract_text(bgr)["status"], "ok")
        np.testing.assert_array_equal(bgr, before)

    def test_grayscale_copy_and_custom_parameters(self):
        before = self.gray.copy()

        def engine(image, **kwargs):
            self.assertEqual(image.ndim, 2)
            image[:] = 0
            self.assertEqual(kwargs, {"lang": "eng+osd", "config": "--psm 3", "timeout": 0.5})
            return "42"

        with (
            patch("modules.ocr.pytesseract.get_languages", return_value=["eng", "osd"]),
            patch("modules.ocr.pytesseract.image_to_string", side_effect=engine),
        ):
            extract_text(self.gray, lang="eng+osd", psm=3, timeout=0.5)
        np.testing.assert_array_equal(self.gray, before)

    def test_missing_second_language_reports_error_before_ocr(self):
        with (
            patch("modules.ocr.pytesseract.get_languages", return_value=["eng"]),
            patch("modules.ocr.pytesseract.image_to_string") as engine,
        ):
            result = extract_text(self.gray, lang="eng+hin")
        engine.assert_not_called()
        self.assertEqual(result["status"], "error")
        self.assertIn("hin", result["error"])

    def test_successful_blank_or_punctuation_is_no_text(self):
        for raw in ("", " \n\t", "--- ...\n"):
            with self.subTest(raw=raw), patch("modules.ocr.pytesseract.image_to_string", return_value=raw):
                result = extract_text(self.gray)
                self.assertEqual(result["status"], "no_text")
                self.assertEqual(result["text"], raw)
                self.assertIsNone(result["error"])

    def test_engine_failures_are_never_no_text(self):
        cases = [(pytesseract.TesseractNotFoundError(), "executable not found"),
                 (pytesseract.TesseractError(1, "Error opening data file missing.traineddata"), "traineddata"),
                 (RuntimeError("Tesseract process timeout"), "timeout"),
                 (OSError("temporary file unavailable"), "I/O failure")]
        for error, message in cases:
            with self.subTest(error=error), patch("modules.ocr.pytesseract.image_to_string", side_effect=error):
                result = extract_text(self.gray)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["text"], "")
                self.assertIn(message, result["error"])

    def test_invalid_arrays_and_settings(self):
        for image in (None, [], np.zeros((0, 2), dtype=np.uint8), np.zeros((2, 2)),
                      np.zeros((2, 2, 4), dtype=np.uint8), np.zeros((2,), dtype=np.uint8)):
            with self.subTest(image=str(image)), self.assertRaises(ValueError):
                extract_text(image)
        for key, values in {"lang": ("", None, "eng --psm 3", "+eng"),
                            "psm": (0, 2, -1, 14, 6.0, True),
                            "timeout": (0, -1, float("nan"), float("inf"), "20", True)}.items():
            for value in values:
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    extract_text(self.gray, **{key: value})


class RealTesseractTests(unittest.TestCase):
    """Do not skip missing setup: SG04 requires the actual system executable."""

    def test_clear_sample_contains_real_title_and_name(self):
        result = extract_text(load_image(ROOT / "dataset/income_certificate/income_certificate_clear.png"))
        self.assertEqual(result["status"], "ok", result)
        self.assertIn("income certificate", result["text"].casefold())
        self.assertIn("asha verma", result["text"].casefold())

    def test_white_page_is_successful_no_text(self):
        result = extract_text(np.full((300, 500), 255, dtype=np.uint8))
        self.assertEqual(result["status"], "no_text", result)
        self.assertIsNone(result["error"])

    def test_real_missing_executable(self):
        with patch("pytesseract.pytesseract.tesseract_cmd", "/nonexistent/dip042-tesseract"):
            result = extract_text(np.full((100, 100), 255, dtype=np.uint8))
        self.assertEqual(result["status"], "error")
        self.assertIn("executable not found", result["error"])

    def test_real_missing_language_data(self):
        result = extract_text(np.full((100, 100), 255, dtype=np.uint8), lang="dip042_missing_language")
        self.assertEqual(result["status"], "error", result)
        self.assertIn("traineddata", result["error"])

    def test_real_timeout(self):
        result = extract_text(np.full((100, 100), 255, dtype=np.uint8), timeout=0.000001)
        self.assertEqual(result["status"], "error", result)
        self.assertIn("timeout", result["error"])


if __name__ == "__main__":
    unittest.main()
