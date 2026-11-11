"""JB03 fictional/reference-record tests: no image processing or OCR is run.

write_fixture_reports() is a test-only reproducible sample export, never a
production provider. app.py must use real OCR records at M01.
"""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from modules.classification import classify_document
from modules.extraction import extract_fields
from modules.readiness import analyze_readiness, render_report


ROOT = Path(__file__).resolve().parents[1]
TYPES = ("income_certificate", "caste_certificate", "marksheet", "identity_proof")
TITLES = ("Income Certificate", "Caste Certificate", "Marksheet", "Identity Proof")


def load_config():
    return json.loads((ROOT / "config/requirements.json").read_text(encoding="utf-8"))


def make_record(doc_type="income_certificate", record_id="fixture-1", text=None,
                status="ok", source="processed"):
    """Build the actual contract shape from authored text, visibly fictional."""
    if text is None:
        title = TITLES[TYPES.index(doc_type)] if doc_type in TYPES else "Unrelated receipt"
        text = (f"FICTIONAL REFERENCE ONLY - NOT REAL OCR\n{title}\n"
                "Student Name: Asha Example\nApplication ID: APP-00041\n"
                "Issue Date: 2026-01-15")
        if doc_type in TYPES[:2]:
            text += "\nCertificate Number: " + ("INC" if doc_type == TYPES[0] else "CST") + "-00017"
    ocr = {"text": text, "status": status, "confidence": None,
           "error": "Fictional test timeout" if status == "error" else None,
           "engine_config": {"lang": "eng", "psm": 6, "timeout": 20}}
    classification = classify_document(text)
    return {
        "id": record_id, "filename": "FICTIONAL_" + record_id + ".png",
        "ocr_original": deepcopy(ocr), "ocr_processed": deepcopy(ocr),
        "ocr_source": source, "ocr": deepcopy(ocr), "classification": classification,
        "fields": extract_fields(text, classification["doc_type"]),
        "processing_parameters": {"fixture_only": True},
    }


def complete_records():
    return [make_record(doc_type, f"fixture-{index}") for index, doc_type in enumerate(TYPES)]


def fixture_report():
    config = load_config()
    config["profile_name"] += " — FICTIONAL FIXTURE EXAMPLE, NOT REAL OCR"
    records = complete_records()
    records[3] = make_record("identity_proof", "fixture-3", text=(
        "FICTIONAL REFERENCE ONLY - NOT REAL OCR\nIdentity Proof\n"
        "Student Name:\nApplication ID: APP-00041"))
    records.append(make_record("income_certificate", "fixture-bad-duplicate", text=(
        "FICTIONAL REFERENCE ONLY - NOT REAL OCR\nIncome Certificate\nStudent Name:")))
    records.append(make_record("unknown", "fixture-unknown"))
    return analyze_readiness(records, config)


def write_fixture_reports():
    """Write only labeled fictional outputs; production functions never save files."""
    report = fixture_report()
    destination = ROOT / "outputs/reports"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "JB03_fixture_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (destination / "JB03_fixture_report.md").write_text(render_report(report), encoding="utf-8")
    return report


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()

    def test_app_checklist_uses_document_details(self):
        config = json.loads((ROOT / "config/document_checklist.json").read_text(encoding="utf-8"))
        records = complete_records()
        records[0]["document_details"] = {"monthly_income": "₹8,000"}
        records[1]["document_details"] = {"caste_category": "SC"}
        records[3]["document_details"] = {"pan_number": "AAAAA0000A"}
        for record in records[:2]:
            record["fields"]["student_name"] = record["fields"]["certificate_number"] = None
        self.assertEqual(analyze_readiness(records, config)["overall_status"], "Ready")
        records[0]["document_details"] = {"monthly_income": None, "annual_income": " "}
        records[3].pop("document_details")  # A holder name alone does not satisfy the PAN check.
        report = analyze_readiness(records, config)
        self.assertEqual(report["overall_status"], "Needs Attention")
        self.assertEqual(report["documents"][0]["missing_required_fields"], ["income_amount"])
        self.assertEqual(report["documents"][3]["missing_required_fields"], ["pan_number"])

    def test_default_config_and_complete_submission(self):
        report = analyze_readiness(complete_records(), self.config)
        self.assertEqual(self.config["required_documents"], {
            "income_certificate": ["student_name", "certificate_number"],
            "caste_certificate": ["student_name", "certificate_number"],
            "marksheet": ["student_name"], "identity_proof": ["student_name"],
        })
        self.assertEqual(self.config["readability"], {"min_alnum_chars": 20})
        self.assertEqual(report["overall_status"], "Ready")
        self.assertEqual((report["submitted_file_count"], report["required_type_count"],
                          report["detected_required_type_count"], report["usable_required_type_count"]), (4, 4, 4, 4))
        self.assertEqual((report["coverage_percent"], report["readiness_percent"]), (100, 100))
        self.assertEqual((report["missing_types"], report["unusable_types"]), ([], []))

    def test_three_of_four_is_75_percent_and_incomplete(self):
        report = analyze_readiness(complete_records()[:3], self.config)
        self.assertEqual((report["coverage_percent"], report["readiness_percent"]), (75, 75))
        self.assertEqual(report["missing_types"], ["identity_proof"])
        self.assertEqual(report["unusable_types"], [])
        self.assertEqual(report["overall_status"], "Incomplete")

    def test_four_detected_three_usable(self):
        report = fixture_report()
        self.assertEqual((report["submitted_file_count"], report["detected_required_type_count"],
                          report["usable_required_type_count"]), (6, 4, 3))
        self.assertEqual((report["coverage_percent"], report["readiness_percent"]), (100, 75))
        self.assertEqual(report["missing_types"], [])
        self.assertEqual(report["unusable_types"], ["identity_proof"])
        self.assertEqual(report["overall_status"], "Needs Attention")
        document = report["documents"][3]
        self.assertTrue(document["readable"])
        self.assertFalse(document["usable"])
        self.assertEqual(document["missing_required_fields"], ["student_name"])

    def test_unreadable_present_type_is_not_missing(self):
        record = make_record(text="Income Certificate")
        record["fields"]["student_name"] = "Asha Example"
        record["fields"]["certificate_number"] = "INC-00017"
        report = analyze_readiness([record], self.config, ["income_certificate"])
        self.assertEqual(report["coverage_percent"], 100)
        self.assertEqual(report["readiness_percent"], 0)
        self.assertEqual(report["missing_types"], [])
        self.assertEqual(report["unusable_types"], ["income_certificate"])
        self.assertFalse(report["documents"][0]["readable"])

    def test_missing_and_unusable_stay_separate_and_incomplete_wins(self):
        record = make_record(text="Income Certificate")
        report = analyze_readiness([record], self.config)
        self.assertEqual(report["missing_types"], list(TYPES[1:]))
        self.assertEqual(report["unusable_types"], ["income_certificate"])
        self.assertEqual(report["overall_status"], "Incomplete")

    def test_duplicates_and_one_good_one_bad_in_either_order(self):
        good = make_record(record_id="good")
        bad = make_record(record_id="bad", text="Income Certificate")
        other_good = make_record(record_id="other-good")
        for records in ([good, bad, other_good], [bad, other_good, good]):
            with self.subTest(order=[r["id"] for r in records]):
                report = analyze_readiness(records, self.config)
                self.assertEqual(report["submitted_file_count"], 3)
                self.assertEqual(report["detected_required_type_count"], 1)
                self.assertEqual(report["usable_required_type_count"], 1)
                self.assertEqual((report["coverage_percent"], report["readiness_percent"]), (25, 25))
                self.assertEqual(report["unusable_types"], [])

    def test_fields_from_two_incomplete_duplicates_are_never_pooled(self):
        name_only = make_record(record_id="name-only", text=(
            "Income Certificate\nStudent Name: Asha Example\nFICTIONAL REFERENCE ONLY"))
        number_only = make_record(record_id="number-only", text=(
            "Income Certificate\nCertificate Number: INC-00017\nFICTIONAL REFERENCE ONLY"))
        report = analyze_readiness([name_only, number_only], self.config, ["income_certificate"])
        self.assertEqual(report["overall_status"], "Needs Attention")
        self.assertEqual(report["readiness_percent"], 0)
        self.assertTrue(all(d["readable"] for d in report["documents"]))
        self.assertTrue(all(not d["usable"] for d in report["documents"]))

    def test_unknown_ambiguous_and_unrequired_remain_visible(self):
        records = [make_record("unknown", "unrelated"),
                   make_record("unknown", "ambiguous", text="Income Certificate and Caste Certificate"),
                   make_record("marksheet", "unrequired")]
        report = analyze_readiness(records, self.config, ["income_certificate"])
        self.assertEqual(report["submitted_file_count"], 3)
        self.assertEqual(report["detected_required_type_count"], 0)
        self.assertEqual(report["usable_required_type_count"], 0)
        self.assertEqual(len(report["documents"]), 3)
        self.assertEqual(report["documents"][1]["doc_type"], "unknown")
        self.assertTrue(report["documents"][1]["classification"]["ambiguous"])
        self.assertTrue(all(not d["is_required"] for d in report["documents"]))

    def test_empty_submission_and_report(self):
        report = analyze_readiness([], self.config)
        self.assertEqual(report["submitted_file_count"], 0)
        self.assertEqual((report["coverage_percent"], report["readiness_percent"]), (0, 0))
        self.assertEqual(report["missing_types"], list(TYPES))
        self.assertEqual(report["unusable_types"], [])
        self.assertEqual(report["overall_status"], "Incomplete")
        self.assertIn("No files submitted.", render_report(report))

    def test_subsets_and_precision(self):
        selected = ["identity_proof", "marksheet", "income_certificate"]
        report = analyze_readiness([make_record()], self.config, selected)
        self.assertEqual(report["required_types"], selected)
        self.assertEqual(report["missing_types"], selected[:2])
        self.assertEqual(report["readiness_percent"], 100 / 3)
        self.assertIn("33.33%", render_report(report))
        self.assertEqual(analyze_readiness([make_record()], self.config,
                                          ["income_certificate"])["overall_status"], "Ready")

    def test_readability_boundary_counts_unicode_alnum_not_punctuation(self):
        self.config["readability"]["min_alnum_chars"] = 20
        for text, readable in (("é" * 19 + "!? \n" * 40, False), ("é" * 20, True)):
            record = make_record("unknown", text=text)
            document = analyze_readiness([record], self.config)["documents"][0]
            self.assertEqual(document["alnum_char_count"], 20 if readable else 19)
            self.assertEqual(document["readable"], readable)
        # The configured minimum changes the result; confidence cannot rescue it.
        record = make_record()
        record["ocr"]["confidence"] = 100
        record["ocr_processed"] = deepcopy(record["ocr"])
        self.config["readability"]["min_alnum_chars"] = 10000
        self.assertFalse(analyze_readiness([record], self.config)["documents"][0]["readable"])

    def test_error_and_no_text_status_override_character_count(self):
        for status in ("error", "no_text"):
            record = make_record(status=status)
            document = analyze_readiness([record], self.config)["documents"][0]
            self.assertGreaterEqual(document["alnum_char_count"], 20)
            self.assertFalse(document["readable"])
            self.assertFalse(document["usable"])
            self.assertTrue(document["problems"])
        blank = make_record("unknown", text="", status="no_text")
        report = analyze_readiness([blank], self.config)
        self.assertEqual(report["submitted_file_count"], 1)
        self.assertEqual(report["documents"][0]["ocr"]["status"], "no_text")

    def test_uses_selected_original_not_bad_processed_result(self):
        record = make_record(source="original")
        record["ocr_processed"] = make_record(status="error")["ocr"]
        report = analyze_readiness([record], self.config, ["income_certificate"])
        self.assertEqual(report["overall_status"], "Ready")
        self.assertEqual(report["documents"][0]["ocr_source"], "original")
        self.assertEqual(report["documents"][0]["ocr_processed"]["status"], "error")
        record["ocr_source"] = "processed"  # Caller must update selected OCR/classification/fields too.
        with self.assertRaisesRegex(ValueError, "ocr_source"):
            analyze_readiness([record], self.config)

    def test_optional_and_configurable_required_fields(self):
        record = make_record("marksheet")
        record["fields"]["application_id"] = None
        record["fields"]["issue_date"] = None
        self.assertEqual(analyze_readiness([record], self.config, ["marksheet"])["overall_status"], "Ready")
        self.config["required_documents"]["marksheet"].append("application_id")
        report = analyze_readiness([record], self.config, ["marksheet"])
        self.assertEqual(report["overall_status"], "Needs Attention")
        self.assertEqual(report["documents"][0]["missing_required_fields"], ["application_id"])
        self.config["required_documents"]["marksheet"] = []
        self.assertEqual(analyze_readiness([record], self.config, ["marksheet"])["overall_status"], "Ready")

    def test_whitespace_fields_and_distinct_student_names(self):
        records = complete_records()
        records[0]["fields"]["student_name"] = " \t\n"
        self.assertEqual(analyze_readiness(records, self.config)["readiness_percent"], 75)
        records[0]["fields"]["student_name"] = "Another Example"
        report = analyze_readiness(records, self.config)
        self.assertEqual(report["overall_status"], "Ready")
        self.assertTrue(any("same student" in limitation for limitation in report["limitations"]))

    def test_same_filename_different_ids_preserved_duplicate_ids_rejected(self):
        records = [make_record(record_id="a"), make_record(record_id="b")]
        records[1]["filename"] = records[0]["filename"]
        report = analyze_readiness(records, self.config)
        self.assertEqual([d["id"] for d in report["documents"]], ["a", "b"])
        records[1]["id"] = "a"
        with self.assertRaisesRegex(ValueError, "Duplicate record ID"):
            analyze_readiness(records, self.config)

    def test_invalid_checklist_selections(self):
        for selection in ([], (), "income_certificate", ["unknown"], ["income_certificate"] * 2,
                          ["not_configured"], [None], [["marksheet"]]):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                analyze_readiness([], self.config, selection)
        del self.config["required_documents"]["marksheet"]
        with self.assertRaises(ValueError):
            analyze_readiness([], self.config, ["marksheet"])

    def test_invalid_configuration(self):
        invalid = [None, {}, [], {**self.config, "extra": 1}]
        for key, values in {
            "profile_name": ("", "  ", None, 5),
            "required_documents": ({}, [], {"unknown": []}, {"typo": []},
                                   {"marksheet": "student_name"}, {"marksheet": ["typo"]},
                                   {"marksheet": ["student_name", "student_name"]},
                                   {"marksheet": [[]]}, {"marksheet": [None]}),
            "readability": ({}, [], {"min_alnum_chars": 0}, {"min_alnum_chars": -1},
                            {"min_alnum_chars": True}, {"min_alnum_chars": 20.5},
                            {"min_alnum_chars": "20"}, {"min_alnum_chars": None},
                            {"min_alnum_chars": 20, "extra": 1}),
        }.items():
            invalid.extend({**self.config, key: value} for value in values)
        for config in invalid:
            with self.subTest(config=config), self.assertRaises(ValueError):
                analyze_readiness([], config)

    def test_malformed_records_fail_clearly_without_silent_fallback(self):
        invalid = [None, {}, {**make_record(), "id": " "}, {**make_record(), "filename": None},
                   {**make_record(), "fields": {}}, {**make_record(), "processing_parameters": []},
                   {**make_record(), "classification": {"doc_type": "typo", "evidence": [], "ambiguous": False}}]
        for key, value in (("text", None), ("status", "success"), ("confidence", float("nan")),
                           ("confidence", True), ("error", 5), ("engine_config", {})):
            record = make_record()
            record["ocr"][key] = value
            record["ocr_processed"] = deepcopy(record["ocr"])
            invalid.append(record)
        record = make_record()
        record["fields"]["student_name"] = 123
        invalid.append(record)
        record = make_record()
        record["processing_parameters"]["image"] = object()
        invalid.append(record)
        for record in invalid:
            with self.subTest(record=record), self.assertRaises(ValueError):
                analyze_readiness([record], self.config)
        for records in (None, {}, "records"):
            with self.subTest(records=records), self.assertRaises(ValueError):
                analyze_readiness(records, self.config)

    def test_report_preserves_raw_data_is_independent_and_serializable(self):
        records = complete_records()
        originals, original_config = deepcopy(records), deepcopy(self.config)
        records[0]["display_image"] = object()  # Ignored display data never enters JSON.
        report = analyze_readiness(records, self.config)
        self.assertEqual(self.config, original_config)
        self.assertEqual({k: v for k, v in records[0].items() if k != "display_image"}, originals[0])
        json.loads(json.dumps(report, allow_nan=False))
        for key in originals[0]:
            self.assertEqual(report["documents"][0][key], originals[0][key])
        self.assertNotIn("display_image", report["documents"][0])
        report["documents"][0]["fields"]["student_name"] = "Changed Example"
        report["configuration"]["required_documents"]["marksheet"].clear()
        self.assertEqual(records[0]["fields"], originals[0]["fields"])
        self.assertEqual(self.config, original_config)

    def test_markdown_contains_counts_fields_text_settings_and_limits(self):
        report = fixture_report()
        original = deepcopy(report)
        text = render_report(report)
        for expected in ("FICTIONAL FIXTURE EXAMPLE, NOT REAL OCR", "Needs Attention", "Submitted files: 6",
                         "100.00%", "75.00%", "Detected but unusable types: Identity Proof",
                         "Asha Example", "INC-00017", "Not Found / Unreadable", "Processing settings:",
                         "Selected OCR text:", "authenticity", "official eligibility", "minimum"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)
        self.assertEqual(report, original)

    def test_markdown_keeps_filename_and_ocr_markup_as_data(self):
        record = make_record(text="Unrelated receipt\n````\n# OCR heading\n<script>test</script>")
        record["filename"] = "[link](https://example.invalid)\n# heading.png"
        text = render_report(analyze_readiness([record], self.config))
        self.assertIn("`````text\n" + record["ocr"]["text"] + "\n`````", text)
        self.assertIn("\\[link\\]", text)
        self.assertNotIn("### [link]", text)

    def test_committed_fixture_exports_match_reproducible_results(self):
        report = fixture_report()
        actual_json = json.loads((ROOT / "outputs/reports/JB03_fixture_report.json").read_text(encoding="utf-8"))
        actual_markdown = (ROOT / "outputs/reports/JB03_fixture_report.md").read_text(encoding="utf-8")
        self.assertEqual(actual_json, report)
        self.assertEqual(actual_markdown, render_report(report))


if __name__ == "__main__":
    unittest.main()
