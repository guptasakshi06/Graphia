"""Image input and independent SG02 DIP operations for Project 042.

All processing helpers return fresh uint8 arrays. The combined pipeline,
thresholding and morphology are scheduled for SG03.
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
