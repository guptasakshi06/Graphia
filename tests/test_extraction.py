"""JB02 tests of authored reference text; these do not run or measure OCR."""

import json
from pathlib import Path
import unittest

from modules.classification import classify_document
from modules.extraction import extract_fields


FIELD_KEYS = {"student_name", "certificate_number", "application_id", "issue_date"}
KNOWN_TYPES = ("income_certificate", "caste_certificate", "marksheet", "identity_proof")
EMPTY_FIELDS = dict.fromkeys(FIELD_KEYS)


class ExtractionTests(unittest.TestCase):
    def test_pan_card_uses_the_explicit_holder_label(self):
        heading = "INCOME TAX DEPARTMENT\nPermanent Account Number Card\n"
        for name in ("Name: Asha Example", "Name\nAsha Example", "नाम / Name: Asha Example"):
            with self.subTest(name=name):
                text = heading + name + "\nFather's Name\nBela Example"
                self.assertEqual(classify_document(text)["doc_type"], "identity_proof")
                self.assertEqual(extract_fields(text, "identity_proof"), {
                    **EMPTY_FIELDS, "student_name": "Asha Example",
                })
        parent_only = heading + "Name\nFather's Name\nBela Example"
        self.assertEqual(extract_fields(parent_only, "identity_proof"), EMPTY_FIELDS)
        self.assertEqual(extract_fields(heading + "Name\nSignature", "identity_proof"), EMPTY_FIELDS)
        self.assertEqual(extract_fields(heading + "Name: Asha Example\nName: Bela Example",
                                        "identity_proof"), EMPTY_FIELDS)
        self.assertEqual(classify_document("Apply for a permanent account number card")["doc_type"], "unknown")
        self.assertEqual(classify_document("Income Certificate\n" + heading)["doc_type"], "unknown")

    def test_bilingual_income_uses_applicant_and_certificate_labels(self):
        heading = "कार्यालय तहसीलदार द्वारा प्रदत्त आय प्रमाण-पत्र\n"
        numbers = "आवेदन क्र०: 000000000000004\nप्रमाणपत्र संख्या: 000000000042\n"
        for label, name in (("Applicant Name", "Asha Example"),
                            ("आवेदक का नाम / Applicant Name", "Asha Example"),
                            ("1. उम्मीदवार का नाम", "आशा उदाहरण")):
            with self.subTest(label=label):
                text = heading + numbers + f"{label}: {name}\nपिता का नाम: Other Example"
                self.assertEqual(classify_document(text)["doc_type"], "income_certificate")
                self.assertEqual(extract_fields(text, "income_certificate"), {
                    **EMPTY_FIELDS, "student_name": name, "certificate_number": "000000000042",
                })
        self.assertEqual(classify_document("आय प्रमाण-पत्र हेतु आवेदन-पत्र")["doc_type"], "unknown")
        application_only = heading + "आवेदन क्र०: 000000000000004\nपिता का नाम: Other Example"
        self.assertEqual(extract_fields(application_only, "income_certificate"), EMPTY_FIELDS)
        damaged_label = heading + "प्रमाणपत्र Feat: 000000000042"
        self.assertEqual(extract_fields(damaged_label, "income_certificate")["certificate_number"],
                         "000000000042")
        for line in ("आवेदन Feat: 000000000042", "प्रमाणपत्र Feat 000000000042",
                     "प्रमाणपत्र Feat: 000000000042 000000000043"):
            self.assertIsNone(extract_fields(heading + line, "income_certificate")["certificate_number"])
        narrative = heading + numbers + "This is to certify that Shri Asha Example daughter of Other Example"
        self.assertEqual(extract_fields(narrative, "income_certificate")["student_name"], "Asha Example")

    def test_obc_form_uses_holder_sentence_and_labeled_certificate_number(self):
        heading = ("FORM OF CERTIFICATE TO BE PRODUCED BY\n"
                   "OTHER BACKWARD CLASSES")
        body = (
            "\nआवेदन क्र० 000000000000001\nप्रमाणपत्र क०.. 000000000042\n"
            "This is to certify that Asha\nExample son/daughter of Other Example."
        )
        text = heading + body
        self.assertEqual(classify_document(text)["doc_type"], "caste_certificate")
        self.assertEqual(extract_fields(text, "caste_certificate"), {
            **EMPTY_FIELDS, "student_name": "Asha Example", "certificate_number": "000000000042",
        })
        self.assertEqual(classify_document("Other Backward Classes" + body)["doc_type"], "unknown")
        self.assertEqual(extract_fields("Caste Certificate" + body, "caste_certificate"), EMPTY_FIELDS)
        self.assertEqual(classify_document("Income Certificate\n" + text)["doc_type"], "unknown")

        conflicts = text + (
            "\nप्रमाण पत्र क्र०: 000000000043\n"
            "This is to certify that Bela Example daughter of Other Example."
        )
        self.assertEqual(extract_fields(conflicts, "caste_certificate"), EMPTY_FIELDS)

        application_only = text.replace("प्रमाणपत्र क०.. 000000000042\n", "")
        self.assertIsNone(extract_fields(application_only, "caste_certificate")["certificate_number"])

    def test_all_reference_cases_through_classifier_and_extractor(self):
        fixtures = json.loads(
            (Path(__file__).parent / "fixtures" / "rule_cases.json").read_text(encoding="utf-8")
        )
        for case in fixtures["cases"]:
            with self.subTest(case=case["id"]):
                classification = classify_document(case["text"])
                self.assertEqual(classification, case["expected_classification"])
                actual = extract_fields(case["text"], classification["doc_type"])
                self.assertEqual(actual, case["expected_fields"])
                self.assertEqual(set(actual), FIELD_KEYS)
                self.assertTrue(all(v is None or isinstance(v, str) for v in actual.values()))

    def test_blank_and_unlabeled_values_for_every_type(self):
        for doc_type in KNOWN_TYPES + ("unknown",):
            for text in ("", " \t\r\n", "Asha Example\n00017\nAPP-00041\n2026-01-15"):
                with self.subTest(doc_type=doc_type, text=text):
                    self.assertEqual(extract_fields(text, doc_type), EMPTY_FIELDS)

    def test_unknown_with_complete_labels_stays_empty(self):
        text = ("Student Name: Asha Example\nCertificate Number: INC-00017\n"
                "Application ID: APP-00041\nIssue Date: 2026-01-15")
        self.assertEqual(extract_fields(text, "unknown"), EMPTY_FIELDS)
        ambiguous = "Income Certificate\nCaste Certificate\n" + text
        doc_type = classify_document(ambiguous)["doc_type"]
        self.assertEqual(extract_fields(ambiguous, doc_type), EMPTY_FIELDS)

    def test_each_known_type_extracts_its_applicable_fields(self):
        for doc_type in KNOWN_TYPES:
            prefix = "CST" if doc_type == "caste_certificate" else "INC"
            text = (f"Certificate Number: {prefix}-2026-0042\nStudent Name: Asha Example\n"
                    "Application ID: APP-2026-0101\nIssue Date: 2026-01-15")
            with self.subTest(doc_type=doc_type):
                expected = {
                    "student_name": "Asha Example", "application_id": "APP-2026-0101",
                    "issue_date": "2026-01-15", "certificate_number": None,
                }
                if doc_type in ("income_certificate", "caste_certificate"):
                    expected["certificate_number"] = f"{prefix}-2026-0042"
                self.assertEqual(extract_fields(text, doc_type), expected)

    def test_empty_labels_never_consume_following_lines(self):
        for separator in ("\n", "\r\n", "\r"):
            for label in ("Student Name", "Certificate Number", "Application ID", "Issue Date"):
                text = separator.join([label + ": \t", "Asha Example", "00017", "2026-01-15"])
                with self.subTest(separator=repr(separator), label=label):
                    self.assertEqual(extract_fields(text, "income_certificate"), EMPTY_FIELDS)

    def test_no_substring_or_generic_label_match(self):
        for label in ("Father Name", "Name", "Old Student Name", "NotStudent Name"):
            with self.subTest(label=label):
                self.assertEqual(extract_fields(label + ": Asha Example", "marksheet"), EMPTY_FIELDS)
        for text in ("Old Certificate Number: 00017", "Receipt Number: 00017",
                     "Student Name Asha Example", "Issue Date = 2026-01-15",
                     "Student ID: 00041", "Date of Birth: 2026-01-15"):
            with self.subTest(text=text):
                self.assertEqual(extract_fields(text, "income_certificate"), EMPTY_FIELDS)

    def test_supported_label_variants_and_case(self):
        for label in ("Certificate Number", "Certificate No", "Certificate No.", "CERTIFICATE\tNO."):
            with self.subTest(label=label):
                self.assertEqual(
                    extract_fields("\t" + label + " :  CST-00028 \t", "caste_certificate")["certificate_number"],
                    "CST-00028",
                )

    def test_ids_remain_strings_with_leading_zeroes(self):
        for value in ("000041", "APP-00041", "app-2026-000041"):
            with self.subTest(value=value):
                self.assertEqual(
                    extract_fields("Application ID: " + value, "marksheet")["application_id"], value
                )

    def test_malformed_ids_are_not_partially_salvaged(self):
        invalid = ("INC", "INC-", "INC--0017", "INC-00O17", "INC-00017?", "INC-00017 trailing",
                   "INC -00017", "INC-00017/2", "CST-00017", "00017 9", "2026-01-15",
                   "１２３４", "INC-0017 Application ID: APP-0041", "0" * 65)
        for value in invalid:
            with self.subTest(value=value):
                result = extract_fields("Certificate Number: " + value, "income_certificate")
                self.assertIsNone(result["certificate_number"])
        for value in ("APP--0041", "APP-00O41", "INC-0041", "APP-0041?", "APP-0041 trailing"):
            with self.subTest(value=value):
                self.assertIsNone(extract_fields("Application ID: " + value, "marksheet")["application_id"])

    def test_calendar_dates_and_iso_format_only(self):
        for value in ("2024-02-29", "2000-02-29", "2026-01-15"):
            with self.subTest(value=value):
                self.assertEqual(extract_fields("Issue Date: " + value, "marksheet")["issue_date"], value)
        for value in ("2026-02-29", "1900-02-29", "2026-02-30", "2026-13-01", "2026-00-10",
                      "2026-01-00", "0000-01-01", "2026-1-5", "01/02/2026", "15-01-2026",
                      "20260115", "2026-W03-4", "2026-01-15 extra", "2026-01-15T00:00:00"):
            with self.subTest(value=value):
                self.assertIsNone(extract_fields("Issue Date: " + value, "marksheet")["issue_date"])

    def test_names_keep_case_and_supported_punctuation(self):
        for raw, expected in (("Asha   Example", "Asha Example"), ("A. Example-Sen", "A. Example-Sen"),
                              ("Dev O'Example", "Dev O'Example"), ("ASHA EXAMPLE", "ASHA EXAMPLE")):
            with self.subTest(raw=raw):
                self.assertEqual(extract_fields("Student Name: " + raw, "marksheet")["student_name"], expected)
        for value in ("Asha Examp1e", "???", "Asha_Example", "Asha Example Application ID: APP-0041",
                      "A" * 81, "A", "N/A", "Unknown", "Not Found", "Not Found / Unreadable", "None"):
            with self.subTest(value=value):
                self.assertIsNone(extract_fields("Student Name: " + value, "marksheet")["student_name"])

    def test_duplicate_labels_are_conservative_for_each_field(self):
        cases = (
            ("Student Name", "Asha Example", "Mira Example", "???", "student_name"),
            ("Certificate Number", "INC-00017", "INC-00018", "INC-00O17", "certificate_number"),
            ("Application ID", "APP-00041", "APP-00042", "APP--0041", "application_id"),
            ("Issue Date", "2026-01-15", "2026-01-16", "2026-02-30", "issue_date"),
        )
        for label, first, second, invalid, key in cases:
            for value in (second, invalid, ""):
                for a, b in ((first, value), (value, first)):
                    with self.subTest(field=key, a=a, b=b):
                        text = f"{label}: {a}\n{label}: {b}"
                        self.assertIsNone(extract_fields(text, "income_certificate")[key])
            text = f"{label}: {first}\n{label}: {first}"
            self.assertEqual(extract_fields(text, "income_certificate")[key], first)

    def test_one_bad_field_does_not_hide_an_independent_good_field(self):
        result = extract_fields(
            "Student Name: Asha Example\nCertificate Number: INC-00O17\n"
            "Application ID: APP-00041\nIssue Date: 2026-02-30", "income_certificate"
        )
        self.assertEqual(result, {"student_name": "Asha Example", "certificate_number": None,
                                  "application_id": "APP-00041", "issue_date": None})

    def test_raw_text_is_unchanged_and_results_are_independent(self):
        raw = "\tStudent Name : ASHA   EXAMPLE \r\nApplication ID: 000041"
        snapshot = raw
        first = extract_fields(raw, "marksheet")
        first["student_name"] = "caller edit"
        second = extract_fields(raw, "marksheet")
        self.assertEqual(raw, snapshot)
        self.assertEqual(second["student_name"], "ASHA EXAMPLE")
        self.assertEqual(json.loads(json.dumps(second)), second)

    def test_invalid_callers_raise_clear_errors(self):
        for value in (None, 42, b"Student Name: Asha Example", [], {}):
            with self.subTest(text=value):
                with self.assertRaisesRegex(TypeError, "OCR text as a string"):
                    extract_fields(value, "marksheet")
        for value in (None, 42, [], {}):
            with self.subTest(doc_type=value):
                with self.assertRaisesRegex(TypeError, "doc_type as a string"):
                    extract_fields("", value)
        for value in ("", "Income Certificate", "passport", "UNKNOWN"):
            with self.subTest(doc_type=value):
                with self.assertRaisesRegex(ValueError, "Unsupported document type"):
                    extract_fields("", value)


if __name__ == "__main__":
    unittest.main()
