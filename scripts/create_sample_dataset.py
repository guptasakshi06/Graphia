"""Create eight fictional reference images, transcripts and a contact sheet.

Run from the checkout: .venv/bin/python scripts/create_sample_dataset.py
No OCR or production preprocessing is performed. Reruns reproduce the assets;
visual verification is valid only when hashes match dataset/visual_review.json.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, __version__ as PIL_VERSION


ROOT = Path(__file__).resolve().parents[1]
SIZE = (1400, 1000)  # width, height
LABEL = "SYNTHETIC SAMPLE - NOT AN OFFICIAL DOCUMENT"
FOOTER = "Fictional classroom data. No official validity."
SPECS = [
    ("income_certificate", "Income Certificate", {
        "student_name": "Asha Verma", "certificate_number": "INC-2026-0042",
        "application_id": "APP-2026-0101", "issue_date": "2026-01-15",
    }, ["Annual Family Income: INR 120000", "Purpose: Classroom demonstration"],
     "low_contrast", {"scale": 0.22, "offset": 185}),
    ("caste_certificate", "Caste Certificate", {
        "student_name": "Neel Rao", "certificate_number": "CST-2026-0043",
        "application_id": "APP-2026-0102", "issue_date": "2026-01-16",
    }, ["Category: Fictional demonstration category", "Purpose: Classroom demonstration"],
     "noisy", {"seed": 4201, "sigma": 18.0}),
    ("marksheet", "Marksheet", {
        "student_name": "Mira Sen", "certificate_number": None,
        "application_id": "APP-2026-0103", "issue_date": "2026-01-17",
    }, ["Examination: Sample Semester", "Mathematics: 81 / 100",
        "Computer Science: 87 / 100", "Result: Pass"],
     "slightly_blurred", {"gaussian_radius": 1.2}),
    ("identity_proof", "Identity Proof", {
        "student_name": "Dev Mehta", "certificate_number": None,
        "application_id": "APP-2026-0104", "issue_date": "2026-01-18",
    }, ["Institution: Example Learning Centre", "Student ID: DEMO-042-04"],
     "slightly_blurred", {"gaussian_radius": 1.5}),
]
FIELD_LABELS = {
    "student_name": "Student Name", "certificate_number": "Certificate Number",
    "application_id": "Application ID", "issue_date": "Issue Date",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference_lines(title, fields, details):
    """Return every visible text line in top-to-bottom reading order."""
    return [LABEL, title] + [
        f"{FIELD_LABELS[key]}: {value}"
        for key, value in fields.items() if value is not None
    ] + details + [FOOTER]


def render_document(lines, font_path, bold_path):
    """Draw the whole reference layout with explicit fonts and no hidden text."""
    image = Image.new("RGB", SIZE, "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((30, 30, 1369, 969), outline=(20, 70, 110), width=4)
    for index, line in enumerate(lines):
        size = 30 if index in (0, len(lines) - 1) else 36
        if index == 1:
            size = 48
        font = ImageFont.truetype(str(bold_path if index < 2 else font_path), size)
        x, y = 65, 65 + index * 72
        bounds = draw.textbbox((x, y), line, font=font)
        if bounds[2] > SIZE[0] - 60 or bounds[3] > SIZE[1] - 60:
            raise ValueError(f"Text does not fit on the sample: {line}")
        color = (20, 70, 110) if index < 2 else (25, 25, 25)
        draw.text((x, y), line, fill=color, font=font)
    return image


def degrade(image, condition, settings):
    """Make controlled test conditions, not a production filter pipeline."""
    if condition == "low_contrast":
        pixels = np.asarray(image).astype(np.float32)
        pixels = np.rint(pixels * settings["scale"] + settings["offset"])
        return Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))
    if condition == "noisy":
        rng = np.random.default_rng(settings["seed"])
        noise = rng.normal(0, settings["sigma"], (image.height, image.width, 1))
        pixels = np.rint(np.asarray(image).astype(np.float32) + noise)
        return Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))
    if condition == "slightly_blurred":
        return image.filter(ImageFilter.GaussianBlur(settings["gaussian_radius"]))
    raise ValueError(f"Unknown degradation: {condition}")


def create_dataset(dataset_dir, contact_path, font_dir):
    font_path = font_dir / "DejaVuSans.ttf"
    bold_path = font_dir / "DejaVuSans-Bold.ttf"
    for path in (font_path, bold_path):
        if not path.is_file():
            raise ValueError(f"Font missing: {path}; use --font-dir with DejaVu fonts.")
    reference_dir = dataset_dir / "references"
    reference_dir.mkdir(parents=True, exist_ok=True)
    samples, thumbnails = [], []
    for doc_type, title, fields, details, condition, settings in SPECS:
        lines = reference_lines(title, fields, details)
        clear = render_document(lines, font_path, bold_path)
        for quality, parameters, parent, image in [
            ("clear", {}, None, clear),
            (condition, settings, f"{doc_type}_clear", degrade(clear, condition, settings)),
        ]:
            sample_id = f"{doc_type}_{quality}"
            relative_image = Path(doc_type) / f"{sample_id}.png"
            image_path = dataset_dir / relative_image
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(image_path)
            reference = Path("references") / f"{sample_id}.txt"
            (dataset_dir / reference).write_text("\n".join(lines) + "\n", encoding="utf-8")
            samples.append({
                "id": sample_id, "doc_type": doc_type, "condition": quality,
                "image_path": relative_image.as_posix(),
                "reference_path": reference.as_posix(), "expected_fields": fields,
                "derivative_of": parent, "settings": parameters,
                "width": image.width, "height": image.height,
                "provenance": "Project-created fictional Pillow sample; no real personal data",
                "image_sha256": sha256(image_path),
                "reference_sha256": sha256(dataset_dir / reference),
            })
            thumbnails.append((sample_id, image))

    manifest = {
        "schema_version": 1,
        "purpose": "Synthetic development/evaluation samples, not independent real documents",
        "path_base": "Paths are relative to this manifest's directory",
        "reference_status": "Unverified unless hashes match visual_review.json",
        "visual_review_path": "visual_review.json",
        "generator": {
            "script": "scripts/create_sample_dataset.py", "pillow": PIL_VERSION,
            "numpy": np.__version__, "dimensions_wh": list(SIZE),
            "font_name": font_path.name, "font_sha256": sha256(font_path),
            "bold_font_name": bold_path.name, "bold_font_sha256": sha256(bold_path),
            "noise": "NumPy default_rng; monochrome Gaussian noise; round and clip to uint8",
        },
        "samples": samples,
    }
    (dataset_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    # Adjacent clear/derivative pairs, with full documents (no crop).
    sheet = Image.new("RGB", (1600, 4 * 620), (225, 230, 235))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(font_path), 24)
    for index, (sample_id, image) in enumerate(thumbnails):
        x, y = (index % 2) * 800, (index // 2) * 620
        draw.text((x + 20, y + 12), sample_id, fill="black", font=font)
        sheet.paste(image.resize((784, 560), Image.Resampling.LANCZOS), (x + 8, y + 50))
    contact_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(contact_path)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", type=Path, default=ROOT / "dataset")
    parser.add_argument("--contact-sheet", type=Path,
                        default=ROOT / "outputs/experiments/contact_sheet.png")
    parser.add_argument("--font-dir", type=Path,
                        default=Path("/usr/share/fonts/truetype/dejavu"))
    args = parser.parse_args()
    manifest = create_dataset(args.dataset_dir, args.contact_sheet, args.font_dir)
    print(f"Created {len(manifest['samples'])} fictional samples: {args.dataset_dir}")
    print(f"Contact sheet: {args.contact_sheet}")
    print("Reference text requires visual inspection and matching visual_review.json hashes.")


if __name__ == "__main__":
    main()
