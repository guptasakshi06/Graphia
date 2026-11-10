# SG01 fictional image dataset

Eight PNG images: four clear layouts and four degraded derivatives. These are
project-created fictional classroom documents, visibly labeled synthetic, with
no government emblems, signatures or real personal data. They do not represent
official forms, eligibility rules or independent real-world evaluation cases.

| Type | Fictional name | Certificate number | Degraded condition |
|---|---|---|---|
| Income Certificate | Asha Verma | INC-2026-0042 | Low contrast: round(0.22 × pixel + 185) |
| Caste Certificate | Neel Rao | CST-2026-0043 | Gaussian noise, seed 4201, sigma 18 |
| Marksheet | Mira Sen | Not applicable | Pillow Gaussian blur radius 1.2 |
| Identity Proof | Dev Mehta | Not applicable | Pillow Gaussian blur radius 1.5 |

Every layout includes `Student Name:`, `Application ID:` and `Issue Date:`.
Only certificates include `Certificate Number:`. The reference fields use the
contract's four keys; inapplicable certificate numbers are JSON `null`.
Full transcripts in `references/` contain **every visible line**, including
the synthetic label and disclaimer, in top-to-bottom order with a final newline.
They are reference text, never an OCR result or a production fallback.

`manifest.json` records type, condition, dimensions, relative paths, provenance,
parent sample ID, expected fields, exact settings, library versions, font hashes
and image/reference SHA-256 hashes. All paths are relative to `dataset/`.
Images are RGB PNGs of width 1400 × height 1000. The loader returns their OpenCV
BGR equivalents without resizing at its default 1800-pixel maximum.

Recreate from Sakshi's checkout:

```bash
.venv/bin/python scripts/create_sample_dataset.py
.venv/bin/python -m unittest discover -s tests -p test_preprocessing.py -v
```

The generator uses Ubuntu DejaVu Sans/DejaVu Sans Bold from
`/usr/share/fonts/truetype/dejavu`; `--font-dir` allows the same fonts elsewhere.
It fails clearly if they are absent. Font hashes and pinned Pillow/NumPy versions
are part of reproducibility; different fonts/versions may change raster bytes.
No network, OCR engine or extra dependencies are used by generation.
Reruns overwrite the eight generated image/transcript files and manifest/contact
sheet, but never create a new verification claim. They leave this README and
`visual_review.json` alone. Use `--dataset-dir` and `--contact-sheet` to generate
into temporary paths if comparing changes.

Visual verification lives in `visual_review.json`, separate from generated data.
It records actual assistant inspection, not a student/human review. A reference
is verified only while its image and text hashes match that record. Changed
assets require reinspection; tests deliberately reject stale review hashes.
The contact sheet is `outputs/experiments/contact_sheet.png` relative to the
checkout. SG01 provides no OCR accuracy or application readiness results.
