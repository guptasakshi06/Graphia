"""Verify frozen M02 evidence without modifying owner artifacts or calling OCR.

Run with .venv/bin/python docs/merge/verify_m02.py [--json /tmp/result.json].
The full regression suite separately checks saved pixels, CER, settings and rules.
"""

import argparse
from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path):
    return sha256((ROOT / path).read_bytes()).hexdigest()


def verify():
    from PIL import Image
    from modules.readiness import analyze_readiness, render_report
    from scripts.run_experiments import verified_ocr_samples

    freeze = read_json("docs/merge/M02-freeze.json")
    for commit in (freeze["merged_evidence_commit"], *freeze["owner_cutoffs"].values()):
        subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"],
                       cwd=ROOT, check=True)
    for path, expected in freeze["sha256"].items():
        assert digest(path) == expected, "Frozen file changed: " + path
    for path in freeze["unchanged_production_paths"]:
        subprocess.run(["git", "diff", "--exit-code", freeze["m01_baseline"],
                        "HEAD", "--", path], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL)

    manifest, _, samples = verified_ocr_samples(ROOT / "dataset/manifest.json")
    conditions = Counter(s["condition"] for s in manifest["samples"])
    assert len(samples) == 8 and len({s["doc_type"] for s, _ in samples}) == 4
    assert conditions == {"clear": 4, "low_contrast": 1, "noisy": 1, "slightly_blurred": 2}
    sg = read_json("outputs/experiments/SG05/metrics.json")
    for path, expected in sg["source_sha256"].items():
        assert digest(path) == expected, "Measured source changed: " + path
    assert digest("dataset/manifest.json") == sg["manifest_sha256"]
    assert digest("dataset/visual_review.json") == sg["visual_review_sha256"]
    artifacts = read_json("outputs/experiments/SG05/artifact_sha256.json")
    repeat = read_json("outputs/experiments/SG05_reproducibility.json")
    assert repeat["byte_identical"] and repeat["same_file_set"]
    assert repeat["original_sha256"] == repeat["repeat_sha256"]
    assert len(repeat["original_sha256"]) == 282
    for relative, expected in repeat["original_sha256"].items():
        assert digest("outputs/experiments/SG05/" + relative) == expected
    assert len(artifacts) == 281

    jb_manifest = read_json("outputs/reports/JB05/artifact_manifest.json")
    for entry in jb_manifest:
        assert digest(entry["path"]) == entry["sha256"], entry["path"]
        assert (ROOT / entry["path"]).stat().st_size == entry["bytes"]
    spec = importlib.util.spec_from_file_location(
        "jb05_evidence", ROOT / "outputs/reports/JB05/verify_evidence.py")
    evidence = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evidence)
    evidence.verify()  # Deliberately omit inventory(), which rewrites owner evidence.

    config = read_json("config/requirements.json")
    scenarios = ("single", "complete", "missing", "unusable", "edge_batch",
                 "checklist_subset", "original_source", "changed_settings")
    for scenario in scenarios:
        report = read_json("outputs/reports/JB05/" + scenario + ".json")
        assert report == analyze_readiness(report["documents"], config,
                                           required_types=report["required_types"]), scenario
        md = ROOT / "outputs/reports/JB05" / (scenario + ".md")
        if md.exists():
            assert md.read_text() == render_report(report), scenario
    screenshots = sorted((ROOT / "outputs/screenshots/JB05").glob("*.jpg"))
    assert len(screenshots) == 15
    for path in screenshots:
        with Image.open(path) as picture:
            assert picture.size == (1280, 720)
            picture.verify()
    result = {"status": "PASS", "frozen_files": len(freeze["sha256"]),
              "samples": len(samples), "conditions": dict(conditions),
              "comparison_groups": len(sg["comparison_groups"]),
              "measured_method_rows": len(sg["rows"]),
              "sg05_reproduction_files_identical": 282,
              "browser_scenarios": len(scenarios), "screenshots": len(screenshots),
              "fresh_ocr_calls_in_this_audit": 0,
              "fresh_browser_run_in_this_audit": False}
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    result = verify()
    if args.json:
        args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
