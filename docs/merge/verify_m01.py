"""M01 development smoke: real local OCR, fictional samples, no fixture provider.

Run from the repository root: .venv/bin/python docs/merge/verify_m01.py
This is integration evidence, not final SG05 dataset evaluation.
"""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import app
from modules.readiness import analyze_readiness, render_report


class SampleUpload:
    def __init__(self, path):
        self.path = path
        self.name = path.name

    def getvalue(self):
        return self.path.read_bytes()


def main():
    manifest = json.loads((ROOT / "dataset/manifest.json").read_text())
    samples = [sample for sample in manifest["samples"] if sample["condition"] == "clear"]
    items = app.collect_uploads([
        SampleUpload(ROOT / "dataset" / sample["image_path"]) for sample in samples
    ])
    items.append({"id": "m01-corrupt", "filename": "M01_FICTIONAL_CORRUPT.png",
                  "data": b"invalid image"})
    records, views = app.analyze_uploads(items, {}, "processed", app.load_real_provider())
    config = json.loads((ROOT / "config/requirements.json").read_text())
    report = analyze_readiness(records, config)
    for sample, record in zip(samples, records):
        assert record["classification"]["doc_type"] == sample["doc_type"], record
        assert record["fields"] == sample["expected_fields"], record
        assert record["ocr_original"]["status"] == record["ocr_processed"]["status"] == "ok"
        assert set(views[record["id"]]["stages"]) == set(app.STAGES)
    assert len(samples) == 4
    assert report["submitted_file_count"] == 5
    assert report["detected_required_type_count"] == report["usable_required_type_count"] == 4
    assert report["readiness_percent"] == report["coverage_percent"] == 100
    assert report["overall_status"] == "Ready"
    assert report["documents"][-1]["ocr"]["status"] == "error"
    evidence = ROOT / "docs/merge"
    (evidence / "M01-real-report.json").write_text(json.dumps(report, indent=2) + "\n")
    (evidence / "M01-real-report.md").write_text(render_report(report).rstrip() + "\n")
    print("PASS: 4 real samples / 8 Tesseract calls; expected types/fields; "
          "6 stages each; corrupt file retained; 5 files, 4 detected/usable, Ready at 100%.")


if __name__ == "__main__":
    main()
