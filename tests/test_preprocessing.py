"""SG01 image-boundary and dataset integrity checks; no OCR assertions."""

import hashlib
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from modules.preprocessing import load_image
from scripts.create_sample_dataset import create_dataset


ROOT = Path(__file__).resolve().parents[1]


def encoded(image, format="PNG", **kwargs):
    buffer = BytesIO()
    image.save(buffer, format=format, **kwargs)
    return buffer.getvalue()


class ImageInputTests(unittest.TestCase):
    def test_paths_bytes_bgr_and_independent_result(self):
        payload = encoded(Image.new("RGB", (12, 8), (255, 0, 0)))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "red.png"
            path.write_bytes(payload)
            a, b, c = load_image(path), load_image(str(path)), load_image(payload)
        self.assertEqual(a.shape, (8, 12, 3))
        self.assertEqual(a.dtype, np.uint8)
        np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(a, c)
        self.assertEqual(a[0, 0].tolist(), [0, 0, 255])
        a[:] = 0
        self.assertEqual(c[0, 0].tolist(), [0, 0, 255])

    def test_exif_orientation_moves_pixels(self):
        image = Image.new("RGB", (60, 40), "red")
        image.paste((0, 0, 255), (30, 0, 60, 40))
        exif = Image.Exif()
        exif[274] = 6  # Rotate 90 degrees clockwise for display.
        loaded = load_image(encoded(image, "JPEG", exif=exif, quality=100))
        self.assertEqual(loaded.shape, (60, 40, 3))
        self.assertGreater(int(loaded[5, 20, 2]), 240)  # top red
        self.assertGreater(int(loaded[55, 20, 0]), 240)  # bottom blue

    def test_rgba_and_palette_transparency_on_white(self):
        rgba = Image.new("RGBA", (3, 1), (255, 0, 0, 0))
        rgba.putpixel((1, 0), (255, 0, 0, 128))
        loaded = load_image(encoded(rgba))
        self.assertEqual(loaded[0, 0].tolist(), [255, 255, 255])
        self.assertEqual(loaded[0, 1].tolist(), [127, 127, 255])
        palette = Image.new("P", (2, 2), 0)
        palette.putpalette([255, 0, 0] + [0, 0, 0] * 255)
        loaded = load_image(encoded(palette, transparency=0))
        self.assertTrue(np.all(loaded == 255))

    def test_grayscale_input(self):
        loaded = load_image(encoded(Image.new("L", (4, 5), 83)))
        self.assertEqual(loaded.shape, (5, 4, 3))
        self.assertTrue(np.all(loaded == 83))

    def test_resize_landscape_portrait_and_no_enlargement(self):
        for size, expected in [((2400, 1200), (900, 1800, 3)),
                               ((1200, 2400), (1800, 900, 3)),
                               ((7, 3), (3, 7, 3)),
                               ((3000, 1), (1, 1800, 3))]:
            with self.subTest(size=size):
                self.assertEqual(load_image(encoded(Image.new("RGB", size))).shape, expected)
        self.assertEqual(load_image(encoded(Image.new("RGB", (1400, 1000))), 700).shape,
                         (500, 700, 3))

    def test_invalid_input_and_limit_fail_clearly(self):
        for source in (b"", b"not an image", "/does/not/exist.png", 42, None):
            with self.subTest(source=source), self.assertRaises(ValueError):
                load_image(source)
        payload = encoded(Image.new("RGB", (10, 10)))
        for limit in (0, -1, True, 1.5, "1800", None):
            with self.subTest(limit=limit), self.assertRaisesRegex(ValueError, "positive integer"):
                load_image(payload, limit)
        with patch("modules.preprocessing.MAX_SOURCE_PIXELS", 99):
            with self.assertRaisesRegex(ValueError, "pixel input limit"):
                load_image(payload)
        with self.assertRaises(ValueError):
            load_image(payload[:35])  # truncated PNG


class DatasetTests(unittest.TestCase):
    def test_generator_reproduces_assets_and_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            manifest = create_dataset(destination / "dataset", destination / "contact.png",
                                      Path("/usr/share/fonts/truetype/dejavu"))
            original = json.loads((ROOT / "dataset/manifest.json").read_text())
            self.assertEqual(manifest, original)
            for row in manifest["samples"]:
                for path_key in ("image_path", "reference_path"):
                    relative = row[path_key]
                    self.assertEqual((destination / "dataset" / relative).read_bytes(),
                                     (ROOT / "dataset" / relative).read_bytes())
            self.assertEqual((destination / "contact.png").read_bytes(),
                             (ROOT / "outputs/experiments/contact_sheet.png").read_bytes())

    def test_manifest_images_references_and_review_hashes(self):
        base = ROOT / "dataset"
        manifest = json.loads((base / "manifest.json").read_text())
        review = json.loads((base / "visual_review.json").read_text())
        rows = manifest["samples"]
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({r["id"] for r in rows}), 8)
        self.assertEqual({r["condition"] for r in rows},
                         {"clear", "low_contrast", "noisy", "slightly_blurred"})
        self.assertEqual({r["doc_type"] for r in rows},
                         {"income_certificate", "caste_certificate", "marksheet", "identity_proof"})
        by_id = {r["id"]: r for r in rows}
        for row in rows:
            with self.subTest(sample=row["id"]):
                paths = [base / row["image_path"], base / row["reference_path"]]
                for path, key in zip(paths, ("image_sha256", "reference_sha256")):
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    self.assertEqual(digest, row[key])
                    self.assertEqual(digest, review["samples"][row["id"]][key])
                self.assertEqual(review["samples"][row["id"]]["status"], "visually_verified")
                image = load_image(paths[0])
                np.testing.assert_array_equal(image, load_image(paths[0].read_bytes()))
                self.assertEqual(image.shape, (row["height"], row["width"], 3))
                text = paths[1].read_text()
                self.assertIn("SYNTHETIC SAMPLE", text)
                self.assertIn(row["expected_fields"]["student_name"], text)
                labels = {"student_name": "Student Name", "certificate_number": "Certificate Number",
                          "application_id": "Application ID", "issue_date": "Issue Date"}
                for key, value in row["expected_fields"].items():
                    if value is None:
                        self.assertNotIn(labels[key] + ":", text)
                    else:
                        self.assertIn(f"{labels[key]}: {value}", text)
                if row["doc_type"].endswith("certificate"):
                    self.assertIn("Certificate Number: " + row["expected_fields"]["certificate_number"], text)
                if row["derivative_of"]:
                    parent = by_id[row["derivative_of"]]
                    self.assertEqual(row["expected_fields"], parent["expected_fields"])
                    self.assertEqual(row["reference_sha256"], parent["reference_sha256"])
                    self.assertNotEqual(row["image_sha256"], parent["image_sha256"])


if __name__ == "__main__":
    unittest.main()
