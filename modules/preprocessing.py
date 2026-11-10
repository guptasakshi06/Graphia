"""Image input, DIP helpers and contract-v1 pipeline for Project 042.

All processing helpers return fresh uint8 arrays. Dark text on a light
background is the document convention; morphology explicitly inverts it.
"""

from io import BytesIO
from numbers import Integral, Real
from pathlib import Path
import warnings

import cv2
import numpy as np
from PIL import Image, ImageOps


# Bound decoded input memory as well as the dimensions returned to the caller.
MAX_SOURCE_PIXELS = 40_000_000


def load_image(source, max_dimension=1800):
    """Decode a path or encoded bytes into an independent BGR uint8 array.

    Apply EXIF orientation first, composite transparency on white, then shrink
    only when necessary. INTER_AREA averages source pixels during downsampling.
    No enlargement is performed. Dimensions round to the nearest whole pixel
    (minimum one), so aspect ratio can differ by at most rounding error.
    Invalid sources/options raise ValueError; the input is never modified.
    """
    if (isinstance(max_dimension, bool)
            or not isinstance(max_dimension, Integral) or max_dimension <= 0):
        raise ValueError("max_dimension must be a positive integer.")
    if isinstance(source, bytes):
        encoded = BytesIO(source)
    elif isinstance(source, (str, Path)):
        encoded = source
    else:
        raise ValueError("source must be an image path (str/Path) or encoded bytes.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(encoded) as opened:
                if opened.width * opened.height > MAX_SOURCE_PIXELS:
                    raise ValueError(
                        f"Image exceeds the {MAX_SOURCE_PIXELS:,}-pixel input limit."
                    )
                oriented = ImageOps.exif_transpose(opened)
                # RGBA handles palette transparency and grayscale alpha too.
                rgba = oriented.convert("RGBA")
                white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
                rgb = np.array(Image.alpha_composite(white, rgba).convert("RGB"))
    except (OSError, ValueError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise ValueError(f"Cannot load image: {exc}") from exc

    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    height, width = bgr.shape[:2]
    if max(height, width) > max_dimension:
        scale = int(max_dimension) / max(height, width)
        size = (max(1, round(width * scale)), max(1, round(height * scale)))
        bgr = cv2.resize(bgr, size, interpolation=cv2.INTER_AREA)
    return bgr


def _validate_image(image, channels):
    """Reject unsupported arrays before calling OpenCV."""
    expected = "BGR (height, width, 3)" if channels == 3 else "grayscale (height, width)"
    if (not isinstance(image, np.ndarray) or image.dtype != np.uint8
            or image.ndim != (3 if channels == 3 else 2)
            or image.size == 0 or (channels == 3 and image.shape[2] != 3)):
        raise ValueError(f"image must be a nonempty uint8 {expected} array.")


def _positive_integer(value, name, odd=False):
    if (isinstance(value, bool) or not isinstance(value, Integral)
            or value <= 0 or (odd and value % 2 == 0)):
        qualifier = "positive odd integer" if odd else "positive integer"
        raise ValueError(f"{name} must be a {qualifier}.")
    return int(value)


def to_grayscale(image_bgr):
    """Convert BGR uint8 to gray using ~0.114B + 0.587G + 0.299R."""
    _validate_image(image_bgr, 3)
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)


def denoise_image(gray, method="median", kernel_size=3):
    """Apply one filter to gray, never a Gaussian/median chain.

    Gaussian uses sigmaX=0 (OpenCV derives sigma from kernel size) and
    BORDER_REFLECT_101. Median uses OpenCV's replicated borders. A 1x1
    kernel or method='none' returns an independent unchanged copy.
    """
    _validate_image(gray, 1)
    if not isinstance(method, str) or method not in ("none", "gaussian", "median"):
        raise ValueError("method must be none, gaussian or median.")
    kernel_size = _positive_integer(kernel_size, "kernel_size", odd=True)
    if method == "none" or kernel_size == 1:
        return gray.copy()
    if method == "gaussian":
        return cv2.GaussianBlur(gray, (kernel_size, kernel_size), sigmaX=0,
                                borderType=cv2.BORDER_REFLECT_101)
    return cv2.medianBlur(gray, kernel_size)


def enhance_contrast(gray, method="clahe", clip_limit=2.0, tile_grid_size=(8, 8)):
    """Apply one contrast method directly to gray and record settings at call sites.

    equalize uses a global 256-bin histogram. CLAHE clips local histograms;
    tile_grid_size is the number of tiles (columns, rows), not pixel size.
    CLAHE options are validated even for bypass/global equalization.
    """
    _validate_image(gray, 1)
    if not isinstance(method, str) or method not in ("none", "equalize", "clahe"):
        raise ValueError("method must be none, equalize or clahe.")
    if (isinstance(clip_limit, bool) or not isinstance(clip_limit, Real)
            or not np.isfinite(clip_limit) or clip_limit <= 0):
        raise ValueError("clip_limit must be a positive finite number.")
    if not isinstance(tile_grid_size, (tuple, list)) or len(tile_grid_size) != 2:
        raise ValueError("tile_grid_size must contain two positive integers.")
    grid = tuple(_positive_integer(v, "tile_grid_size") for v in tile_grid_size)
    if method == "none":
        return gray.copy()
    if method == "equalize":
        return cv2.equalizeHist(gray)
    clahe = cv2.createCLAHE(clipLimit=float(clip_limit), tileGridSize=grid)
    return clahe.apply(gray)


def _finite_number(value, name):
    if (isinstance(value, bool) or not isinstance(value, Real)
            or not np.isfinite(value)):
        raise ValueError(f"{name} must be a finite number.")
    return float(value)


def _threshold_settings(method, global_threshold, adaptive_block_size, adaptive_c):
    if not isinstance(method, str) or method not in ("none", "global", "otsu", "adaptive"):
        raise ValueError("threshold must be none, global, otsu or adaptive.")
    if (isinstance(global_threshold, bool) or not isinstance(global_threshold, Integral)
            or not 0 <= global_threshold <= 255):
        raise ValueError("global_threshold must be an integer from 0 to 255.")
    block = _positive_integer(adaptive_block_size, "adaptive_block_size", odd=True)
    if block <= 1:
        raise ValueError("adaptive_block_size must be an odd integer greater than 1.")
    return int(global_threshold), block, _finite_number(adaptive_c, "adaptive_c")


def threshold_image(gray, method="otsu", global_threshold=127,
                    adaptive_block_size=31, adaptive_c=11):
    """Return (image, selected_otsu_threshold), preserving dark text on white.

    Binary rule: intensity > threshold becomes 255; otherwise 0. Otsu selects
    a global cutoff by minimizing within-group variance. Adaptive uses a
    Gaussian-weighted neighborhood mean minus C, with replicated borders.
    The Otsu cutoff is a float only for method='otsu', otherwise None.
    Validate all settings even when bypassed; 'none' is an independent copy.
    """
    _validate_image(gray, 1)
    cutoff, block, constant = _threshold_settings(
        method, global_threshold, adaptive_block_size, adaptive_c)
    if method == "none":
        return gray.copy(), None
    if method == "adaptive":
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, block, constant), None
    flags = cv2.THRESH_BINARY | (cv2.THRESH_OTSU if method == "otsu" else 0)
    selected, result = cv2.threshold(gray, 0 if method == "otsu" else cutoff, 255, flags)
    return result, float(selected) if method == "otsu" else None


def _morphology_settings(method, kernel_size):
    if not isinstance(method, str) or method not in (
            "none", "erosion", "dilation", "opening", "closing"):
        raise ValueError("morphology must be none, erosion, dilation, opening or closing.")
    return _positive_integer(kernel_size, "morph_kernel_size")


def apply_morphology(gray, method="none", kernel_size=2):
    """Operate on inverted (white) text, then restore dark text on white.

    Accept binary or grayscale uint8; grayscale uses neighborhood min/max.
    Rectangular all-ones kernel, one iteration, anchor=(k//2, k//2).
    OpenCV's constant neutral border ignores out-of-image pixels: 255 for
    erosion and 0 for dilation. Even kernels are allowed by contract but
    asymmetric around the anchor and can shift strokes; compare before use.
    Opening = erosion then dilation; closing = dilation then erosion.
    No automatic foreground guessing or extra threshold is performed.
    """
    _validate_image(gray, 1)
    size = _morphology_settings(method, kernel_size)
    if method == "none":
        return gray.copy()
    foreground = cv2.bitwise_not(gray)
    kernel = np.ones((size, size), dtype=np.uint8)
    operation = {"erosion": cv2.MORPH_ERODE, "dilation": cv2.MORPH_DILATE,
                 "opening": cv2.MORPH_OPEN, "closing": cv2.MORPH_CLOSE}[method]
    result = cv2.morphologyEx(foreground, operation, kernel,
                              anchor=(size // 2, size // 2), iterations=1,
                              borderType=cv2.BORDER_CONSTANT)
    return cv2.bitwise_not(result)


def run_pipeline(image_bgr, options=None):
    """Run contract-v1 selected stages; return stages, ocr_input, parameters.

    Only the nine public option keys in TEAM_CONTRACT.md are accepted. All
    values (including inactive stage settings) are validated. Named bypass
    stages and ocr_input are independent copies, so UI changes cannot mutate
    the caller or another stage. Parameters contain resolved JSON-safe settings
    plus fixed algorithm details and the actual selected Otsu cutoff.
    """
    _validate_image(image_bgr, 3)
    defaults = {
        "denoise": "median", "kernel_size": 3, "contrast": "clahe",
        "threshold": "otsu", "global_threshold": 127,
        "adaptive_block_size": 31, "adaptive_c": 11,
        "morphology": "none", "morph_kernel_size": 2,
    }
    if options is not None:
        if not isinstance(options, dict):
            raise ValueError("options must be a dict or None.")
        if any(key not in defaults for key in options):
            raise ValueError("Unknown pipeline option; use the keys in TEAM_CONTRACT.md.")
        defaults.update(options)
    p = defaults
    for key, allowed in (("denoise", ("none", "gaussian", "median")),
                         ("contrast", ("none", "equalize", "clahe"))):
        if not isinstance(p[key], str) or p[key] not in allowed:
            raise ValueError(f"{key} must be one of {', '.join(allowed)}.")
    p["kernel_size"] = _positive_integer(p["kernel_size"], "kernel_size", odd=True)
    p["global_threshold"], p["adaptive_block_size"], p["adaptive_c"] = _threshold_settings(
        p["threshold"], p["global_threshold"], p["adaptive_block_size"], p["adaptive_c"])
    p["morph_kernel_size"] = _morphology_settings(p["morphology"], p["morph_kernel_size"])
    stages = {"original": image_bgr.copy(), "grayscale": to_grayscale(image_bgr)}
    stages["denoised"] = denoise_image(stages["grayscale"], p["denoise"], p["kernel_size"])
    stages["enhanced"] = enhance_contrast(stages["denoised"], p["contrast"])
    stages["thresholded"], selected = threshold_image(
        stages["enhanced"], p["threshold"], p["global_threshold"],
        p["adaptive_block_size"], p["adaptive_c"])
    stages["morphology"] = apply_morphology(
        stages["thresholded"], p["morphology"], p["morph_kernel_size"])
    p.update({"selected_otsu_threshold": selected, "clahe_clip_limit": 2.0,
              "clahe_tile_grid_size": [8, 8], "adaptive_method": "gaussian",
              "morph_kernel_shape": "rectangle", "morph_iterations": 1,
              "morph_anchor_xy": [p["morph_kernel_size"] // 2] * 2,
              "morph_border": "constant neutral (erosion=255, dilation=0)",
              "morph_foreground": "inverted white text; restored after operation",
              "output_polarity": "dark text / light background (input convention)",
              "input_shape": list(image_bgr.shape), "output_shape": list(stages["morphology"].shape)})
    return {"stages": stages, "ocr_input": stages["morphology"].copy(), "parameters": p}
