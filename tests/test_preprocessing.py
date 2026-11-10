"""SG01–SG03 input, numerical DIP, contract and artifact checks; no OCR assertions."""

import hashlib
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from modules.preprocessing import (apply_morphology, denoise_image, enhance_contrast,
                                   load_image, run_pipeline, threshold_image, to_grayscale)
from scripts.create_sample_dataset import create_dataset
from scripts.run_experiments import compare_methods, compare_sg03


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


class GrayscaleFilterContrastTests(unittest.TestCase):
    def test_grayscale_known_color_weights_and_input_preserved(self):
        bgr = np.array([[[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 255]]],
                       dtype=np.uint8)
        before = bgr.copy()
        gray = to_grayscale(bgr)
        np.testing.assert_array_equal(gray, [[29, 150, 76, 255]])
        np.testing.assert_array_equal(bgr, before)
        self.assertEqual(gray.dtype, np.uint8)
        self.assertFalse(np.shares_memory(bgr, gray))

    def test_gaussian_neighborhood_and_median_impulse(self):
        impulse = np.zeros((7, 7), dtype=np.uint8)
        impulse[3, 3] = 240
        gaussian = denoise_image(impulse, "gaussian", 3)
        # Interior 3x3 Gaussian sigma=0 uses [1,2,1]/4 on each axis.
        np.testing.assert_array_equal(gaussian[2:5, 2:5],
                                      [[15, 30, 15], [30, 60, 30], [15, 30, 15]])
        self.assertEqual(int(gaussian.sum()), 240)
        self.assertTrue(np.all(denoise_image(impulse, "median", 3) == 0))
        neighborhood = np.array([[10, 10, 10], [10, 250, 20], [20, 20, 20]], dtype=np.uint8)
        self.assertEqual(int(denoise_image(neighborhood, "median", 3)[1, 1]), 20)
        self.assertEqual(int(impulse[3, 3]), 240)

    def test_filters_preserve_flat_images_shapes_and_bypass_copies(self):
        gray = np.full((13, 11), 83, dtype=np.uint8)
        for method in ("none", "gaussian", "median"):
            for size in (1, 3, 5):
                result = denoise_image(gray, method, size)
                np.testing.assert_array_equal(result, gray)
                self.assertEqual(result.dtype, np.uint8)
                self.assertFalse(np.shares_memory(result, gray))

    def test_equalization_known_mapping_and_clahe_output(self):
        low_contrast = np.tile(np.array([190, 190, 210, 210], dtype=np.uint8), (32, 8))
        before = low_contrast.copy()
        equalized = enhance_contrast(low_contrast, "equalize")
        np.testing.assert_array_equal(equalized[:, :4], np.tile([0, 0, 255, 255], (32, 1)))
        clahe = enhance_contrast(low_contrast, "clahe", 2.0, (8, 8))
        self.assertEqual(clahe.shape, low_contrast.shape)
        self.assertEqual(clahe.dtype, np.uint8)
        self.assertFalse(np.shares_memory(clahe, low_contrast))
        self.assertFalse(np.array_equal(clahe, low_contrast))
        np.testing.assert_array_equal(low_contrast, before)
        bypass = enhance_contrast(low_contrast, "none")
        np.testing.assert_array_equal(bypass, low_contrast)
        self.assertFalse(np.shares_memory(bypass, low_contrast))

    def test_invalid_arrays_methods_and_settings(self):
        for bad in (None, [], np.zeros((0, 2), np.uint8), np.zeros((2, 2), float),
                    np.zeros((2, 2, 1), np.uint8), np.zeros((2, 2, 4), np.uint8)):
            with self.subTest(shape=getattr(bad, "shape", None)):
                for function in (to_grayscale, denoise_image, enhance_contrast):
                    with self.assertRaisesRegex(ValueError, "uint8"):
                        function(bad)
        with self.assertRaises(ValueError):
            to_grayscale(np.zeros((2, 2), np.uint8))
        with self.assertRaises(ValueError):
            denoise_image(np.zeros((2, 2, 3), np.uint8))
        gray = np.zeros((8, 8), np.uint8)
        for bad in (0, -3, 2, True, 3.0, "3", None):
            with self.subTest(kernel=bad), self.assertRaisesRegex(ValueError, "positive odd"):
                denoise_image(gray, "gaussian", bad)
        for bad in ("bad", None, [], 1):
            for function in (denoise_image, enhance_contrast):
                with self.assertRaisesRegex(ValueError, "method"):
                    function(gray, bad)
        for bad in (0, -1, True, float("nan"), float("inf"), "2", None):
            with self.assertRaisesRegex(ValueError, "clip_limit"):
                enhance_contrast(gray, clip_limit=bad)
        for bad in ((0, 8), (8, -1), (True, 8), (2.5, 8), [8], None, "88"):
            with self.assertRaisesRegex(ValueError, "tile_grid_size"):
                enhance_contrast(gray, tile_grid_size=bad)

    def test_comparison_uses_same_gray_not_chained_outputs(self):
        bgr = np.random.default_rng(42).integers(0, 256, (32, 48, 3), dtype=np.uint8)
        before = bgr.copy()
        alternatives = compare_methods(bgr)
        gray = to_grayscale(bgr)
        expected = {"original": bgr, "grayscale": gray,
                    "gaussian": denoise_image(gray, "gaussian"),
                    "median": denoise_image(gray, "median"),
                    "equalized": enhance_contrast(gray, "equalize"),
                    "clahe": enhance_contrast(gray, "clahe")}
        self.assertEqual(set(alternatives), set(expected))
        for name, (image, settings) in alternatives.items():
            np.testing.assert_array_equal(image, expected[name])
            self.assertEqual(image.dtype, np.uint8)
            self.assertFalse(np.shares_memory(image, bgr))
            json.dumps(settings, allow_nan=False)
        np.testing.assert_array_equal(bgr, before)


class ExperimentArtifactTests(unittest.TestCase):
    def test_saved_metrics_images_histograms_and_source_identity(self):
        import cv2

        folder = ROOT / "outputs/experiments/SG02"
        report = json.loads((folder / "metrics.json").read_text())
        manifest = json.loads((ROOT / "dataset/manifest.json").read_text())
        self.assertEqual(report["manifest_sha256"],
                         hashlib.sha256((ROOT / "dataset/manifest.json").read_bytes()).hexdigest())
        self.assertFalse(report["settings"]["alternatives_chained"])
        self.assertEqual(len(report["rows"]), 48)
        self.assertEqual(len({(r["sample_id"], r["method"]) for r in report["rows"]}), 48)
        sample_ids = {sample["id"] for sample in manifest["samples"]}
        self.assertEqual({r["sample_id"] for r in report["rows"]}, sample_ids)
        for row in report["rows"]:
            with self.subTest(sample=row["sample_id"], method=row["method"]):
                image = cv2.imread(str(folder / row["output_image"]), cv2.IMREAD_UNCHANGED)
                self.assertIsNotNone(image)
                self.assertEqual(list(image.shape), row["shape"])
                self.assertEqual(str(image.dtype), row["dtype"])
                gray = to_grayscale(image) if image.ndim == 3 else image
                self.assertAlmostEqual(float(gray.std()), row["grayscale_stddev"], places=10)
                self.assertAlmostEqual(float(gray.mean()), row["grayscale_mean"], places=10)
                np.testing.assert_array_equal(np.bincount(gray.ravel(), minlength=256),
                                              row["histogram_counts"])
                self.assertEqual(sum(row["histogram_counts"]), gray.size)
                self.assertEqual(int(gray.min()), row["grayscale_min"])
                self.assertEqual(int(gray.max()), row["grayscale_max"])
                source = ROOT / "dataset" / row["source_image"]
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), row["source_sha256"])
                if row["method"] == "original":
                    np.testing.assert_array_equal(image, load_image(source))
        for sample_id in sample_ids:
            for name in ("comparison.png", "detail.png", "histograms.png"):
                with Image.open(folder / sample_id / name) as figure:
                    figure.verify()



class ThresholdMorphologyPipelineTests(unittest.TestCase):
    def test_global_boundary_and_bypass(self):
        gray = np.array([[0, 90, 127, 128, 180, 255]], np.uint8)
        result, selected = threshold_image(gray, "global")
        np.testing.assert_array_equal(result, [[0, 0, 0, 255, 255, 255]])
        self.assertIsNone(selected)
        for cutoff, expected in ((0, [[0, 255, 255, 255, 255, 255]]),
                                 (255, [[0, 0, 0, 0, 0, 0]])):
            np.testing.assert_array_equal(threshold_image(gray, "global", cutoff)[0], expected)
        bypass, selected = threshold_image(gray, "none")
        np.testing.assert_array_equal(bypass, gray)
        self.assertFalse(np.shares_memory(bypass, gray))
        self.assertIsNone(selected)

    def test_otsu_separates_two_groups_and_reports_cutoff(self):
        gray = np.tile(np.array([40, 40, 200, 200], np.uint8), (16, 4))
        before = gray.copy()
        result, cutoff = threshold_image(gray)
        self.assertEqual(cutoff, 40.0)
        np.testing.assert_array_equal(result, np.where(gray == 40, 0, 255))
        np.testing.assert_array_equal(gray, before)
        for value in (0, 83, 255):
            flat = np.full((3, 5), value, np.uint8)
            result, cutoff = threshold_image(flat)
            self.assertEqual(cutoff, 0.0)
            self.assertTrue(np.all(result == (0 if value == 0 else 255)))

    def test_adaptive_retains_dark_line_under_uneven_background(self):
        gray = np.tile(np.linspace(100, 240, 101, dtype=np.uint8), (51, 1))
        gray[24:27, :] -= 50
        before = gray.copy()
        adaptive, cutoff = threshold_image(gray, "adaptive", adaptive_block_size=15, adaptive_c=7)
        self.assertIsNone(cutoff)
        self.assertTrue(np.all(adaptive[25] == 0))
        self.assertTrue(np.all(adaptive[5] == 255))
        # A global cutoff loses the brighter end of the same text line.
        global_result, _ = threshold_image(gray, "global")
        self.assertEqual(int(global_result[25, -1]), 255)
        np.testing.assert_array_equal(gray, before)

    def test_morphology_known_geometry_polarity_and_no_mutation(self):
        gray = np.full((15, 15), 255, np.uint8)
        gray[5:10, 5:10] = 0
        before = gray.copy()
        for method, extent in (("erosion", (6, 9)), ("dilation", (4, 11)),
                               ("opening", (5, 10)), ("closing", (5, 10))):
            expected = np.full_like(gray, 255)
            expected[extent[0]:extent[1], extent[0]:extent[1]] = 0
            result = apply_morphology(gray, method, 3)
            np.testing.assert_array_equal(result, expected)
            self.assertEqual(result[0, 0], 255)
            self.assertEqual(result[7, 7], 0)
            self.assertFalse(np.shares_memory(result, gray))
        np.testing.assert_array_equal(gray, before)
        bypass = apply_morphology(gray)
        np.testing.assert_array_equal(bypass, gray)
        self.assertFalse(np.shares_memory(bypass, gray))

    def test_opening_removes_speck_closing_fills_hole_and_thin_stroke_loss(self):
        gray = np.full((17, 17), 255, np.uint8)
        gray[5:12, 5:12] = 0
        gray[2, 2] = 0
        self.assertEqual(apply_morphology(gray, "opening", 3)[2, 2], 255)
        gray[8, 8] = 255
        self.assertEqual(apply_morphology(gray, "closing", 3)[8, 8], 0)
        thin = np.full((9, 9), 255, np.uint8)
        thin[2:7, 4] = 0
        self.assertTrue(np.all(apply_morphology(thin, "erosion", 3) == 255))
        self.assertTrue(np.all(apply_morphology(thin, "opening", 3) == 255))

    def test_even_kernel_anchor_borders_and_grayscale(self):
        gray = np.full((7, 7), 255, np.uint8)
        gray[3, 3] = 0
        expected = np.full_like(gray, 255)
        expected[3:5, 3:5] = 0  # 2x2 anchor is (1, 1), not centered symmetrically.
        np.testing.assert_array_equal(apply_morphology(gray, "dilation", 2), expected)
        gray[:] = 0
        for method in ("erosion", "dilation", "opening", "closing"):
            self.assertTrue(np.all(apply_morphology(gray, method, 2) == 0))
            self.assertTrue(np.all(apply_morphology(255 - gray, method, 2) == 255))
            np.testing.assert_array_equal(apply_morphology(gray, method, 1), gray)
        ramp = np.tile(np.array([40, 80, 120, 160, 200], np.uint8), (5, 1))
        self.assertEqual(apply_morphology(ramp, "erosion", 3)[2, 2], 160)
        self.assertEqual(apply_morphology(ramp, "dilation", 3)[2, 2], 80)

    def test_pipeline_defaults_exact_keys_shapes_values_and_json(self):
        bgr = np.random.default_rng(42).integers(0, 256, (43, 61, 3), dtype=np.uint8)
        before = bgr.copy()
        result = run_pipeline(bgr)
        self.assertEqual(set(result), {"stages", "ocr_input", "parameters"})
        stages, p = result["stages"], result["parameters"]
        self.assertEqual(list(stages), ["original", "grayscale", "denoised", "enhanced",
                                        "thresholded", "morphology"])
        defaults = {"denoise": "median", "kernel_size": 3, "contrast": "clahe",
                    "threshold": "otsu", "global_threshold": 127, "adaptive_block_size": 31,
                    "adaptive_c": 11, "morphology": "none", "morph_kernel_size": 2}
        for key, value in defaults.items():
            self.assertEqual(p[key], value)
        expected_gray = to_grayscale(bgr)
        expected_denoised = denoise_image(expected_gray)
        expected_enhanced = enhance_contrast(expected_denoised)
        expected_thresholded, selected = threshold_image(expected_enhanced)
        for key, expected in (("original", before), ("grayscale", expected_gray),
                              ("denoised", expected_denoised), ("enhanced", expected_enhanced),
                              ("thresholded", expected_thresholded), ("morphology", expected_thresholded)):
            np.testing.assert_array_equal(stages[key], expected)
            self.assertEqual(stages[key].dtype, np.uint8)
        self.assertEqual(p["selected_otsu_threshold"], selected)
        self.assertEqual(p["clahe_tile_grid_size"], [8, 8])
        np.testing.assert_array_equal(result["ocr_input"], expected_thresholded)
        arrays = [bgr, *stages.values(), result["ocr_input"]]
        for i, left in enumerate(arrays):
            for right in arrays[i + 1:]:
                self.assertFalse(np.shares_memory(left, right))
        np.testing.assert_array_equal(bgr, before)
        json.dumps(p, allow_nan=False)

    def test_pipeline_bypass_options_unchanged_and_numpy_settings_json(self):
        bgr = np.full((2, 3, 3), 83, np.uint8)
        options = {"denoise": "none", "contrast": "none", "threshold": "none",
                   "morphology": "none", "kernel_size": np.int64(3),
                   "adaptive_c": np.float32(-2.5), "morph_kernel_size": np.int64(2)}
        before = options.copy()
        result = run_pipeline(bgr, options)
        self.assertEqual(options, before)
        for key, image in result["stages"].items():
            self.assertTrue(np.all(image == 83))
        self.assertIsNone(result["parameters"]["selected_otsu_threshold"])
        json.dumps(result["parameters"], allow_nan=False)
        result["ocr_input"][:] = 0
        self.assertTrue(np.all(result["stages"]["morphology"] == 83))
        for denoise in ("none", "gaussian", "median"):
            for contrast in ("none", "equalize", "clahe"):
                for threshold in ("none", "global", "otsu", "adaptive"):
                    for morphology in ("none", "erosion", "dilation", "opening", "closing"):
                        result = run_pipeline(bgr, {"denoise": denoise, "contrast": contrast,
                                                   "threshold": threshold, "morphology": morphology})
                        self.assertEqual(result["ocr_input"].shape, (2, 3))
                        self.assertEqual(result["ocr_input"].dtype, np.uint8)
        # This is API branch coverage on tiny input, not a dataset parameter search.

    def test_invalid_options_are_rejected_even_when_stage_bypassed(self):
        bgr = np.zeros((5, 5, 3), np.uint8)
        gray = bgr[:, :, 0]
        bad_values = {"denoise": ["bad", [], None], "contrast": ["bad", 1, None],
                      "threshold": ["bad", {}, None], "morphology": ["bad", [], None],
                      "kernel_size": [0, 2, True, 3.0], "global_threshold": [-1, 256, True, 1.0],
                      "adaptive_block_size": [0, 1, 2, True, 3.0],
                      "adaptive_c": [True, "11", None, float("nan"), float("inf")],
                      "morph_kernel_size": [0, -1, True, 2.0]}
        for key, values in bad_values.items():
            for bad in values:
                options = {"denoise": "none", "contrast": "none", "threshold": "none",
                           "morphology": "none", key: bad}
                with self.subTest(key=key, value=bad), self.assertRaises(ValueError):
                    run_pipeline(bgr, options)
        for options in ([], "otsu", 0, {"typo": 3}, {1: 2}):
            with self.assertRaises(ValueError):
                run_pipeline(bgr, options)
        for image in (None, np.zeros((5, 5), np.uint8), np.zeros((5, 5, 3), float)):
            with self.assertRaises(ValueError):
                run_pipeline(image)
        for image in (None, [], bgr, gray.astype(float), np.zeros((0, 2), np.uint8)):
            for helper in (threshold_image, apply_morphology):
                with self.assertRaises(ValueError):
                    helper(image)
        for kwargs in ({"method": []}, {"global_threshold": 256}, {"adaptive_block_size": 1},
                       {"adaptive_c": float("nan")}):
            with self.assertRaises(ValueError):
                threshold_image(gray, **kwargs)
        for method, size in (("bad", 2), ([], 2), ("none", 0)):
            with self.assertRaises(ValueError):
                apply_morphology(gray, method, size)

    def test_saved_sg03_artifacts_match_recomputed_outputs_and_sources(self):
        import cv2
        folder = ROOT / "outputs/experiments/SG03"
        report = json.loads((folder / "metrics.json").read_text())
        manifest_bytes = (ROOT / "dataset/manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        self.assertEqual(report["manifest_sha256"], hashlib.sha256(manifest_bytes).hexdigest())
        self.assertEqual(len(report["rows"]), 72)
        self.assertEqual(len({(r["sample_id"], r["method"]) for r in report["rows"]}), 72)
        self.assertEqual(len(report["pipelines"]), 8)
        for sample in manifest["samples"]:
            source = ROOT / "dataset" / sample["image_path"]
            expected, pipeline = compare_sg03(load_image(source))
            rows = [r for r in report["rows"] if r["sample_id"] == sample["id"]]
            self.assertEqual({r["method"] for r in rows}, set(expected))
            for row in rows:
                path = folder / row["output_image"]
                image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
                np.testing.assert_array_equal(image, expected[row["method"]][0])
                self.assertEqual(row["parameters"], expected[row["method"]][1])
                self.assertEqual(row["shape"], list(image.shape))
                self.assertEqual(row["dtype"], str(image.dtype))
                self.assertEqual(row["is_binary"], bool(np.isin(image, [0, 255]).all()))
                self.assertEqual(row["dark_pixel_count"], int(np.count_nonzero(image < 128)))
                self.assertEqual(row["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
                self.assertEqual(row["output_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            saved = next(p for p in report["pipelines"] if p["sample_id"] == sample["id"])
            self.assertEqual(saved["parameters"], pipeline["parameters"])
            for stage, path in saved["stage_images"].items():
                np.testing.assert_array_equal(cv2.imread(str(folder / path), cv2.IMREAD_UNCHANGED),
                                              pipeline["stages"][stage])
            for figure in ("thresholds", "thresholds_detail", "morphology", "morphology_detail"):
                with Image.open(folder / sample["id"] / f"{figure}.png") as image:
                    image.verify()

if __name__ == "__main__":
    unittest.main()
