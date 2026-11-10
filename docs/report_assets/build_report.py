#!/usr/bin/env python3
"""Build the editable Project 042 report from docs/project_report.md."""

import argparse
from pathlib import Path
import re

from PIL import Image
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor


DOCS = Path(__file__).resolve().parents[1]
WIDTH = 6.63
BOLD = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")
IMAGE = re.compile(r"!\[([^\]]+)\]\(([^)]+)\)")


def append_xml(parent, tag, **attributes):
    element = OxmlElement(f"w:{tag}")
    for key, value in attributes.items():
        element.set(qn(f"w:{key}"), str(value))
    parent.append(element)
    return element


def write_inline(paragraph, value):
    """Preserve emphasis and show readable citation labels in Word."""
    for part in BOLD.split(value):
        if not part:
            continue
        if part.startswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("`"):
            paragraph.add_run(part[1:-1])
        elif part.startswith("[") and "](" in part:
            paragraph.add_run(part[1:part.index("](")])
        else:
            paragraph.add_run(part)


def configure(doc):
    section = doc.sections[0]
    section.page_height, section.page_width = Mm(297), Mm(210)
    section.top_margin, section.bottom_margin = Mm(19), Mm(17)
    section.left_margin = section.right_margin = Mm(20.8)
    section.footer_distance = Mm(8)
    section.different_first_page_header_footer = True
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.add_run("Project 042  |  ").font.size = Pt(9)
    append_xml(footer._p, "fldSimple", instr="PAGE")

    settings = {
        "Normal": (11, False, 0, 6, 1.13),
        "Title": (31, True, 0, 20, 1.06),
        "Heading 1": (17, True, 8, 5, 1.10),
        "Heading 2": (13, True, 7, 4, 1.10),
        "Caption": (10, False, 3, 8, 1.10),
        "List Bullet": (11, False, 0, 3, 1.11),
    }
    for name, (size, bold, before, after, spacing) in settings.items():
        style = doc.styles[name]
        style.font.name = "Carlito"
        style.font.size = Pt(size)
        style.font.bold = bold
        style.font.italic = False
        style.font.color.rgb = RGBColor(0, 0, 0)
        fmt = style.paragraph_format
        fmt.space_before, fmt.space_after = Pt(before), Pt(after)
        fmt.line_spacing = spacing
    for tag in ("w:pBdr",):
        for el in doc.styles["Title"]._element.xpath(f".//{tag}"):
            el.getparent().remove(el)
    doc.styles["Caption"].paragraph_format.keep_with_next = False
    doc.styles["Caption"].paragraph_format.keep_together = True
    doc.core_properties.title = (
        "Document Intelligence for Application Readiness and Missing Requirement Detection"
    )
    doc.core_properties.subject = "Project 042 College Project Report"
    doc.core_properties.author = "Sakshi Gupta and Jigisha Baiswar"


def make_table(doc, lines):
    """Create a fixed-width, editable Word table with expandable rows."""
    rows = [[v.strip() for v in line.strip("|").split("|")] for line in lines]
    rows = [rows[0], *rows[2:]]
    ratios = {
        2: (.31, .69),
        5: (.34, .10, .20, .16, .20),
        8: (.22, .075, .103, .082, .103, .102, .105, .21),
    }[len(rows[0])]
    total = sum(ratios)
    widths = [Inches(WIDTH * ratio / total) for ratio in ratios]
    table = doc.add_table(rows=len(rows), cols=len(widths))
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders = append_xml(table._tbl.tblPr, "tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        append_xml(borders, side, val="single", sz=6, color="D9D9D9")
    margins = append_xml(table._tbl.tblPr, "tblCellMar")
    for side, size in (("top", 44), ("bottom", 44), ("left", 85), ("right", 85)):
        append_xml(margins, side, w=size, type="dxa")
    for col, width in zip(table.columns, widths):
        col.width = width
    for index, values in enumerate(rows):
        row = table.rows[index]
        trpr = row._tr.get_or_add_trPr()
        append_xml(trpr, "cantSplit")
        if index == 0:
            append_xml(trpr, "tblHeader")
        for j, value in enumerate(values):
            cell = row.cells[j]
            cell.width = widths[j]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            append_xml(cell._tc.get_or_add_tcPr(), "shd",
                       fill="E9EDF1" if index == 0 else ("F5F7F9" if index % 2 == 0 else "FFFFFF"))
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.06
            if j > 0 and len(widths) > 2 and not (len(widths) == 8 and j == 7):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            write_inline(p, value)
            for run in p.runs:
                run.font.size = Pt(9 if len(widths) == 8 else 10)
                if index == 0:
                    run.bold = True
    after = doc.add_paragraph()
    after.paragraph_format.space_after = Pt(0)
    after.paragraph_format.line_spacing = Pt(5)
    after.add_run().font.size = Pt(4)


def make_figure(doc, source, description, relative):
    path = (source.parent / relative).resolve(strict=True)
    with Image.open(path) as image:
        w, h = image.size
    width = min(WIDTH, 3.65 * w / h)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_after = Pt(0)
    shape = p.add_run().add_picture(str(path), width=Inches(width))
    shape._inline.docPr.set("descr", description)


def build(source, output):
    doc = Document()
    configure(doc)
    lines = source.read_text(encoding="utf-8").splitlines()
    i = 0
    cover = True
    pending_break = False
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line == "<!-- pagebreak -->":
            cover, pending_break = False, True
            continue
        if line.startswith("|"):
            table = [line]
            while i < len(lines) and lines[i].startswith("|"):
                table.append(lines[i])
                i += 1
            make_table(doc, table)
            continue
        if match := IMAGE.fullmatch(line):
            make_figure(doc, source, *match.groups())
            continue
        if line.startswith("# "):
            p = doc.add_paragraph(line[2:].replace("Missing-Requirement", "Missing Requirement"), "Title")
            p.paragraph_format.space_before = Pt(82)
        elif line.startswith("## "):
            p = doc.add_paragraph(line[3:], "Heading 1")
        elif line.startswith("### "):
            p = doc.add_paragraph(line[4:], "Heading 2")
        else:
            style = "Caption" if line.startswith(("**Figure", "**Table")) else (
                "List Bullet" if line.startswith("- ") else "Normal"
            )
            p = doc.add_paragraph(style=style)
            write_inline(p, line[2:] if line.startswith(("- ", "> ")) else line)
            if line.startswith("**Table"):
                p.paragraph_format.keep_with_next = True
            if line.startswith("> "):
                p.paragraph_format.left_indent = Inches(.12)
                for run in p.runs:
                    run.italic = True
        if pending_break:
            p.paragraph_format.page_break_before = True
            pending_break = False
        if cover:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if line.startswith("**College"):
                p.paragraph_format.space_after = Pt(33)
            elif line.startswith("College:"):
                p.paragraph_format.space_before = Pt(21)
    doc.save(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DOCS / "project_report.md")
    parser.add_argument("--output", type=Path, default=DOCS / "project_report.docx")
    args = parser.parse_args()
    build(args.source, args.output)
