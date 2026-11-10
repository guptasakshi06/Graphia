"""Reproduce SG02 comparisons. Run with this checkout's .venv/bin/python.

Each alternative starts from the same loaded image/grayscale image. No OCR,
thresholding or morphology is executed. Only fictional manifest samples are
saved; this is not an upload storage path.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # Support execution from outside the checkout.

from modules.preprocessing import (  # noqa: E402
    denoise_image, enhance_contrast, load_image, to_grayscale,
)


def compare_methods(image_bgr, kernel_size=3, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Return independent alternatives with explicit JSON-safe parameters."""
    gray = to_grayscale(image_bgr)
    grid = list(tile_grid_size)
    return {
        "original": (image_bgr.copy(), {"operation": "none"}),
        "grayscale": (gray, {"conversion": "BGR2GRAY"}),
        "gaussian": (denoise_image(gray, "gaussian", kernel_size), {
            "input": "grayscale", "kernel_size": int(kernel_size), "sigma_x": 0,
            "border": "BORDER_REFLECT_101"}),
        "median": (denoise_image(gray, "median", kernel_size), {
            "input": "grayscale", "kernel_size": int(kernel_size),
            "border": "BORDER_REPLICATE"}),
        "equalized": (enhance_contrast(gray, "equalize"), {
            "input": "grayscale", "method": "equalize", "histogram_bins": 256}),
        "clahe": (enhance_contrast(gray, "clahe", clip_limit, tile_grid_size), {
            "input": "grayscale", "method": "clahe", "clip_limit": float(clip_limit),
            "tile_grid_size": grid}),
    }


def _gray(image):
    return to_grayscale(image) if image.ndim == 3 else image


def save_comparison(alternatives, destination, title, crop=None):
    """Use identical 0..255 display ranges and common crop for fair comparison."""
    fig, axes = plt.subplots(2, 3, figsize=(15, 4) if crop else (15, 8),
                             constrained_layout=True)
    for ax, (name, (image, _)) in zip(axes.flat, alternatives.items()):
        if crop:
            x0, y0, x1, y1 = crop
            image = image[y0:y1, x0:x1]
        if image.ndim == 3:
            ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), interpolation="nearest")
        else:
            ax.imshow(image, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        ax.set_title(name)
        ax.axis("off")
    fig.suptitle(title)
    fig.savefig(destination, dpi=120)
    plt.close(fig)


def save_histograms(alternatives, destination, title):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4), constrained_layout=True)
    for ax, names in zip(axes, (("grayscale", "gaussian", "median"),
                                ("grayscale", "equalized", "clahe"))):
        for name in names:
            pixels = _gray(alternatives[name][0])
            counts = np.bincount(pixels.ravel(), minlength=256)
            ax.plot(np.arange(256), counts, label=name, linewidth=1)
        ax.set(xlabel="Intensity (0=black, 255=white)", ylabel="Pixel count (log scale)",
               xlim=(0, 255), yscale="log")
        ax.legend()
    fig.suptitle(title + " — 256-bin histograms; color original uses grayscale baseline")
    fig.savefig(destination, dpi=120)
    plt.close(fig)


def run_experiments(manifest_path, output_dir, kernel_size=3, clip_limit=2.0,
                    tile_grid_size=(8, 8)):
    """Save six-method metrics and figures for every hash-verified sample."""
    manifest_path, output_dir = Path(manifest_path), Path(output_dir)
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for sample in manifest["samples"]:
        path = manifest_path.parent / sample["image_path"]
        image_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if image_hash != sample["image_sha256"]:
            raise ValueError(f"Source image hash differs from manifest: {path}")
        original = load_image(path, max_dimension=1800)
        before = original.copy()
        alternatives = compare_methods(original, kernel_size, clip_limit, tile_grid_size)
        if not np.array_equal(original, before):
            raise RuntimeError("Comparison modified its input image.")
        sample_dir = output_dir / sample["id"]
        sample_dir.mkdir(exist_ok=True)
        title = f"{sample['id']} | independent alternatives | fictional sample"
        save_comparison(alternatives, sample_dir / "comparison.png", title)
        # Shared sample layout: name and certificate/application/date labels.
        crop = (65, 190, 1100, 420)
        save_comparison(alternatives, sample_dir / "detail.png", title + " | same text crop", crop)
        save_histograms(alternatives, sample_dir / "histograms.png", sample["id"])
        for method, (image, parameters) in alternatives.items():
            relative = Path(sample["id"]) / f"{method}.png"
            if not cv2.imwrite(str(output_dir / relative), image):
                raise OSError(f"Could not write {relative}")
            gray = _gray(image)
            counts = np.bincount(gray.ravel(), minlength=256)
            rows.append({
                "sample_id": sample["id"], "condition": sample["condition"],
                "source_image": sample["image_path"], "source_sha256": image_hash,
                "method": method, "parameters": parameters,
                "shape": list(image.shape), "dtype": str(image.dtype),
                "grayscale_stddev": float(np.std(gray, dtype=np.float64, ddof=0)),
                "grayscale_mean": float(np.mean(gray, dtype=np.float64)),
                "grayscale_min": int(gray.min()), "grayscale_max": int(gray.max()),
                "histogram_counts": counts.tolist(), "output_image": relative.as_posix(),
            })
    report = {
        "sprint": "SG02", "purpose": "DIP comparison only; no OCR results",
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "versions": {"numpy": np.__version__, "opencv": cv2.__version__,
                     "matplotlib": matplotlib.__version__},
        "settings": {"max_dimension": 1800, "kernel_size": int(kernel_size),
                     "clahe_clip_limit": float(clip_limit), "clahe_tile_grid_size": list(tile_grid_size),
                     "detail_crop_xyxy": [65, 190, 1100, 420], "alternatives_chained": False},
        "contrast_definition": "Population standard deviation of grayscale intensities (ddof=0); not OCR accuracy",
        "rows": rows,
    }
    (output_dir / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    columns = [key for key in rows[0] if key not in ("histogram_counts", "shape")]
    with (output_dir / "metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row[key], sort_keys=True)
                             if key == "parameters" else row[key] for key in columns})
    print(f"SG02: saved {len(rows)} measured rows for {len(manifest['samples'])} samples to {output_dir}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "dataset/manifest.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/experiments/SG02")
    parser.add_argument("--kernel-size", type=int, default=3)
    parser.add_argument("--clip-limit", type=float, default=2.0)
    parser.add_argument("--tile-grid-size", type=int, nargs=2, default=(8, 8), metavar=("COLS", "ROWS"))
    args = parser.parse_args()
    try:
        run_experiments(args.manifest, args.output_dir, args.kernel_size,
                        args.clip_limit, args.tile_grid_size)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Experiment error: {exc}\n")


if __name__ == "__main__":
    main()
