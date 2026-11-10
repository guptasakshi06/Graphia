#!/usr/bin/env python3
"""Check report content and embedded evidence against the frozen M02 files."""

import csv
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

from docx import Document

DOCS = Path(__file__).resolve().parents[1]
ROOT = DOCS.parent
SG05 = ROOT / "outputs/experiments/SG05"
JB05 = ROOT / "outputs/reports/JB05"
SECTION_NAMES = (
    "Abstract", "Introduction", "Problem Statement", "Objectives", "Existing Approach",
    "Proposed Methodology", "System Architecture", "Implementation",
    "Digital Image Processing Techniques", "Experimental Results", "Limitations",
    "Future Scope", "Conclusion", "References",
)
METHOD_LABELS = {
    "equalized": "Global equalization",
    "clahe": "CLAHE",
    "global": "Global threshold",
    "otsu": "Otsu",
    "adaptive": "Adaptive threshold",
    "pipeline_default": "Fixed default pipeline",
}


def table_rows(table):
    return [[cell.text for cell in row.cells] for row in table.rows]


def main():
    source = (DOCS / "project_report.md").read_text()
    viva = (DOCS / "viva_sakshi.md").read_text()
    docx_path = DOCS / "project_report.docx"
    doc = Document(docx_path)
    assert re.findall(r"^## (.+)$", source, re.M) == list(SECTION_NAMES)
    assert [p.text for p in doc.paragraphs if p.style.name == "Heading 1"] == list(SECTION_NAMES)
    assert len(re.findall(r"^\d+\. \*\*", viva, re.M)) == 15
    for name in ("Sakshi Gupta", "Jigisha Baiswar"):
        assert name in source and any(name in p.text for p in doc.paragraphs)

    with (SG05 / "summary.csv").open(newline="") as handle:
        summary = list(csv.DictReader(handle))
    methods = []
    for row in summary:
        name = row["method"]
        cer = float(row["pooled_cer"])
        assert row["total_reference_characters"] == "2190"
        methods.append([
            METHOD_LABELS.get(name, name.capitalize()), row["total_edits"],
            f"{cer:.9f}" if cer else "0",
            f'{row["type_correct"]}/{row["type_denominator"]}',
            f'{row["present_field_correct"]}/{row["present_field_count"]}',
        ])
    assert len(methods) == 14
    assert table_rows(doc.tables[1])[1:] == methods

    scenarios = (
        "single", "complete", "missing", "unusable", "edge_batch",
        "checklist_subset", "original_source", "changed_settings",
    )
    fields = (
        "submitted_file_count", "detected_required_type_count", "usable_required_type_count",
        "required_type_count", "coverage_percent", "readiness_percent", "overall_status",
    )
    browser = []
    for scenario in scenarios:
        download = json.loads((JB05 / f"{scenario}.json").read_text())
        values = [download[field] for field in fields]
        browser.append([scenario.replace("_", " ").capitalize(), *map(str, values[:4]),
                        *(f"{percent:g}%" for percent in values[4:6]), values[6]])
    assert table_rows(doc.tables[2])[1:] == browser

    freeze = json.loads((DOCS / "merge/M02-freeze.json").read_text())["sha256"]
    figures = re.findall(r"^!\[([^\]]+)\]\(([^)]+)\)$", source, re.M)
    hashes = set()
    frozen_count = 0
    diagrams = set()
    for alt, relative in figures:
        path = (DOCS / relative).resolve(strict=True)
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        repo_path = path.relative_to(ROOT).as_posix()
        if repo_path.startswith("docs/diagrams/"):
            diagrams.add(repo_path)
        else:
            assert freeze[repo_path] == sha, repo_path
            frozen_count += 1
        hashes.add(sha)
    assert diagrams == {"docs/diagrams/architecture.png", "docs/diagrams/workflow.png"}
    with ZipFile(docx_path) as archive:
        embedded = {
            hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist() if name.startswith("word/media/")
        }
    assert frozen_count == 6 and embedded == hashes and len(doc.inline_shapes) == len(figures)
    assert [shape._inline.docPr.get("descr") for shape in doc.inline_shapes] == [
        alt for alt, _ in figures
    ]
    for md in (source, viva):
        for target in re.findall(r"\]\(([^)]+)\)", md):
            if not target.startswith(("http://", "https://")):
                assert (DOCS / target).exists(), target
    print("PASS: 14 required sections; both authors; 15 viva questions; Markdown links resolve.")
    print("PASS: 14 DOCX result rows match frozen SG05 and eight browser rows match JB05.")
    print("PASS: six frozen images and both final diagrams are embedded byte for byte with matching alternative text.")


if __name__ == "__main__":
    main()
