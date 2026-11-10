"""Reproduce SG02 or SG03 comparisons. Run with this checkout's .venv/bin/python.

SG02 alternatives start from the same grayscale input. SG03 thresholds share
grayscale input; morphology alternatives share its Otsu result. No OCR is run.
Only fictional manifest samples are saved; this is not an upload storage path.
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
    apply_morphology, denoise_image, enhance_contrast, load_image,
    run_pipeline, threshold_image, to_grayscale,
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


def compare_sg03(image_bgr):
    """Three independent thresholds, four independent Otsu morphologies, one pipeline."""
    gray = to_grayscale(image_bgr)
    alternatives = {"grayscale": (gray, {"input": "original", "conversion": "BGR2GRAY"})}
    for method in ("global", "otsu", "adaptive"):
        image, selected = threshold_image(gray, method)
        alternatives[method] = (image, {
            "input": "grayscale", "threshold": method, "global_threshold": 127,
            "adaptive_block_size": 31, "adaptive_c": 11,
            "adaptive_method": "gaussian", "selected_otsu_threshold": selected})
    for method in ("erosion", "dilation", "opening", "closing"):
        alternatives[method] = (apply_morphology(alternatives["otsu"][0], method, 2), {
            "input": "otsu", "morphology": method, "morph_kernel_size": 2,
            "kernel_shape": "rectangle", "iterations": 1, "anchor_xy": [1, 1],
            "border": "constant neutral (erosion=255, dilation=0)",
            "foreground": "inverted white text; restored after operation"})
    pipeline = run_pipeline(image_bgr)
    alternatives["pipeline_default"] = (pipeline["ocr_input"], pipeline["parameters"])
    return alternatives, pipeline


def save_sg03_comparison(alternatives, names, destination, title, crop=None):
    """Fixed range and common crop, with no unused panels or clipped labels."""
    fig, axes = plt.subplots(1, len(names), figsize=(4 * len(names), 3 if crop else 5),
                             constrained_layout=True, squeeze=False)
    for ax, name in zip(axes.flat, names):
        image = alternatives[name][0]
        if crop:
            x0, y0, x1, y1 = crop
            image = image[y0:y1, x0:x1]
        ax.imshow(image, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        ax.set_title(name)
        ax.axis("off")
    fig.suptitle(title)
    fig.savefig(destination, dpi=120)
    plt.close(fig)


def run_sg03_experiments(manifest_path, output_dir):
    """Save actual threshold/morphology outputs and every default pipeline stage."""
    manifest_path, output_dir = Path(manifest_path), Path(output_dir)
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows, pipelines = [], []
    for sample in manifest["samples"]:
        path = manifest_path.parent / sample["image_path"]
        image_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if image_hash != sample["image_sha256"]:
            raise ValueError(f"Source image hash differs from manifest: {path}")
        original = load_image(path)
        before = original.copy()
        alternatives, pipeline = compare_sg03(original)
        np.testing.assert_array_equal(original, before)
        sample_dir = output_dir / sample["id"]
        sample_dir.mkdir(exist_ok=True)
        for group, names in (("thresholds", ["grayscale", "global", "otsu", "adaptive"]),
                             ("morphology", ["otsu", "erosion", "dilation", "opening", "closing"])):
            title = f"{sample['id']} | {group} | fictional sample"
            save_sg03_comparison(alternatives, names, sample_dir / f"{group}.png", title)
            save_sg03_comparison(alternatives, names, sample_dir / f"{group}_detail.png",
                                  title + " | common crop", (65, 190, 1100, 420))
        stage_paths = {}
        for name, image in pipeline["stages"].items():
            relative = Path(sample["id"]) / f"stage_{name}.png"
            if not cv2.imwrite(str(output_dir / relative), image):
                raise OSError(f"Could not write {relative}")
            stage_paths[name] = relative.as_posix()
        pipelines.append({"sample_id": sample["id"], "parameters": pipeline["parameters"],
                          "stage_images": stage_paths})
        for method, (image, settings) in alternatives.items():
            relative = Path(sample["id"]) / f"{method}.png"
            if not cv2.imwrite(str(output_dir / relative), image):
                raise OSError(f"Could not write {relative}")
            rows.append({"sample_id": sample["id"], "condition": sample["condition"],
                         "source_image": sample["image_path"], "source_sha256": image_hash,
                         "method": method, "parameters": settings,
                         "shape": list(image.shape), "dtype": str(image.dtype),
                         "dark_pixel_count": int(np.count_nonzero(image < 128)),
                         "dark_pixel_definition": "intensity < 128; not text accuracy",
                         "is_binary": bool(np.isin(image, [0, 255]).all()),
                         "output_image": relative.as_posix(),
                         "output_sha256": hashlib.sha256((output_dir / relative).read_bytes()).hexdigest()})
    report = {"sprint": "SG03", "purpose": "DIP demonstration only; no OCR results",
              "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
              "versions": {"numpy": np.__version__, "opencv": cv2.__version__,
                           "matplotlib": matplotlib.__version__},
              "settings": {"max_dimension": 1800, "detail_crop_xyxy": [65, 190, 1100, 420],
                           "threshold_input": "grayscale", "morphology_input": "otsu(grayscale)",
                           "pipeline_candidate": "contract-v1 defaults; morphology bypassed"},
              "rows": rows, "pipelines": pipelines}
    (output_dir / "metrics.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    with (output_dir / "metrics.csv").open("w", newline="") as handle:
        columns = list(rows[0])
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})
    print(f"SG03: saved {len(rows)} measured rows, {len(pipelines)} pipelines to {output_dir}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprint", choices=("SG02", "SG03"), default="SG02")
    parser.add_argument("--manifest", type=Path, default=ROOT / "dataset/manifest.json")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--kernel-size", type=int, default=3)
    parser.add_argument("--clip-limit", type=float, default=2.0)
    parser.add_argument("--tile-grid-size", type=int, nargs=2, default=(8, 8), metavar=("COLS", "ROWS"))
    args = parser.parse_args()
    try:
        output_dir = args.output_dir or ROOT / "outputs/experiments" / args.sprint
        if args.sprint == "SG03":
            if (args.kernel_size, args.clip_limit, tuple(args.tile_grid_size)) != (3, 2.0, (8, 8)):
                raise ValueError("SG03 comparisons use fixed documented settings; SG02 flags apply to SG02.")
            run_sg03_experiments(args.manifest, output_dir)
        else:
            run_experiments(args.manifest, output_dir, args.kernel_size,
                            args.clip_limit, args.tile_grid_size)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Experiment error: {exc}\n")


if __name__ == "__main__":
    main()
