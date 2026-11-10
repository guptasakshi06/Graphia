"""Local Tesseract OCR, independent of Streamlit and reference transcripts."""

from numbers import Integral, Real
import re

import cv2
import numpy as np
import pytesseract


def extract_text(image, lang="eng", psm=6, timeout=20):
    """Return contract-v1 raw text, status, error and resolved engine settings.

    Accept BGR or 2D grayscale uint8 arrays; the caller's pixels stay unchanged.
    Invalid arguments raise ValueError (programming/input errors). Engine/setup,
    language-data, I/O and timeout failures return status='error'. Blank or
    punctuation-only successful output is 'no_text'; raw output is retained.
    PSM 0 (orientation only) and 2 (unimplemented) cannot produce OCR text.
    Confidence is None: this single text call does not measure confidence or
    accuracy. No transcripts, test fixtures, network calls or fallback text.
    """
    if (not isinstance(image, np.ndarray) or image.dtype != np.uint8
            or image.size == 0 or not (image.ndim == 2
                or (image.ndim == 3 and image.shape[2] == 3))):
        raise ValueError("image must be a nonempty uint8 grayscale or BGR array.")
    if not isinstance(lang, str) or not re.fullmatch(r"[A-Za-z0-9_]+(?:\+[A-Za-z0-9_]+)*", lang):
        raise ValueError("lang must be a language name or + separated language names, e.g. eng.")
    if (isinstance(psm, bool) or not isinstance(psm, Integral)
            or psm not in (1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)):
        raise ValueError("psm must be a text segmentation integer: 1 or 3 through 13.")
    if (isinstance(timeout, bool) or not isinstance(timeout, Real)
            or not np.isfinite(timeout) or timeout <= 0):
        raise ValueError("timeout must be a positive finite number of seconds.")
    result = {"text": "", "status": "error", "confidence": None, "error": None,
              "engine_config": {"lang": lang, "psm": int(psm), "timeout": float(timeout)}}
    # Pytesseract interprets 3-channel arrays as RGB, unlike OpenCV's BGR.
    prepared = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if image.ndim == 3 else image.copy()
    try:
        text = pytesseract.image_to_string(prepared, lang=lang,
                                          config=f"--psm {int(psm)}", timeout=float(timeout))
    except pytesseract.TesseractNotFoundError:
        result["error"] = "Tesseract executable not found. Install tesseract-ocr and ensure it is on PATH."
    except pytesseract.TesseractError as exc:
        # Preserve the engine's diagnostic, including missing .traineddata.
        result["error"] = f"Tesseract OCR failed (check engine/language data): {exc}"
    except RuntimeError as exc:
        result["error"] = f"Tesseract OCR timeout or runtime failure: {exc}"
    except OSError as exc:
        result["error"] = f"Tesseract OCR I/O failure: {exc}"
    else:
        result["text"] = text
        result["status"] = "ok" if any(char.isalnum() for char in text) else "no_text"
    return result
