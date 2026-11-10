"""Image input for Project 042. DIP operations are added in SG02/SG03."""

from io import BytesIO
from numbers import Integral
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
