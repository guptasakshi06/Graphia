"""JB01 rule tests using fictional reference text, never measured OCR output."""

import itertools
import json
from pathlib import Path
import unittest

from modules.classification import classify_document


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "rule_cases.json"
KNOWN_TITLES = {
    "income_certificate": "Income Certificate",
    "caste_certificate": "Caste Certificate",
    "marksheet": "Marksheet",
    "identity_proof": "Identity Proof",
}
FIELD_KEYS = {"student_name", "certificate_number", "application_id", "issue_date"}


class ClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_reference_cases(self):
        for case in self.fixtures["cases"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    classify_document(case["text"]), case["expected_classification"]
                )

    def test_fixture_contract_and_jb02_reference_values(self):
        self.assertIn("not measured OCR", self.fixtures["description"])
        cases = self.fixtures["cases"]
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        self.assertEqual(
            {case["expected_classification"]["doc_type"] for case in cases},
            set(KNOWN_TITLES) | {"unknown"},
        )
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertIsInstance(case["text"], str)
                self.assertEqual(set(case["expected_fields"]), FIELD_KEYS)
                for value in case["expected_fields"].values():
                    self.assertTrue(value is None or isinstance(value, str))
        income = next(case for case in cases if case["id"] == "income_reference")
        self.assertEqual(income["expected_fields"]["certificate_number"], "INC-00017")

    def test_all_titles_ignore_case_and_whitespace(self):
        for doc_type, title in KNOWN_TITLES.items():
            for variant in (title.lower(), title.upper(), " \t\n".join(title.split())):
                with self.subTest(doc_type=doc_type, text=variant):
                    result = classify_document("\n " + variant + " \t")
                    self.assertEqual(result["doc_type"], doc_type)
                    self.assertFalse(result["ambiguous"])
                    self.assertEqual(result["evidence"], [title.lower()])

    def test_every_pair_of_competing_types_is_unknown(self):
        for first, second in itertools.combinations(KNOWN_TITLES.values(), 2):
            with self.subTest(first=first, second=second):
                # Repetition must not outvote a conflicting document title.
                result = classify_document((first + "\n") * 5 + second)
                self.assertEqual(result["doc_type"], "unknown")
                self.assertTrue(result["ambiguous"])
                self.assertEqual(set(result["evidence"]), {first.lower(), second.lower()})

    def test_title_phrases_must_have_word_boundaries(self):
        for title in KNOWN_TITLES.values():
            for text in ("prefix" + title, title + "suffix", title.replace(" ", "-")):
                # A single-word title has no internal space to replace.
                if text == title:
                    continue
                with self.subTest(text=text):
                    self.assertEqual(classify_document(text), {
                        "doc_type": "unknown", "evidence": [], "ambiguous": False,
                    })

    def test_raw_text_retained_and_evidence_is_fresh(self):
        raw_text = "  INCOME\nCertificate\nStudent Name: Asha Example  "
        original = raw_text
        first = classify_document(raw_text)
        first["evidence"].append("caller added text")
        second = classify_document(raw_text)
        self.assertEqual(raw_text, original)
        self.assertEqual(second["evidence"], ["income certificate"])
        self.assertEqual(set(second), {"doc_type", "evidence", "ambiguous"})
        json.dumps(second)  # Contract result can be put into a JSON report.

    def test_no_title_from_fields_or_unrelated_digits(self):
        result = classify_document(
            "Student Name: Asha Example\nCertificate Number: INC-00017\n"
            "Application ID: APP-00041\nIssue Date: 2026-01-15\n48000"
        )
        self.assertEqual(result, {"doc_type": "unknown", "evidence": [], "ambiguous": False})

    def test_non_string_input_reports_caller_error(self):
        for invalid in (None, 42, b"Income Certificate", [], {}):
            with self.subTest(value=invalid):
                with self.assertRaisesRegex(TypeError, "OCR text as a string"):
                    classify_document(invalid)


if __name__ == "__main__":
    unittest.main()
