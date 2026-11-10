"""Conservative extraction for supported document layouts.

Most values follow a supported label on the same line. The supported OBC form
also identifies the holder in a certification sentence. Callers retain the
original OCR text separately.
"""

from datetime import date
import re

from modules.classification import OBC_CERTIFICATE_HEADING


FIELD_KEYS = ("student_name", "certificate_number", "application_id", "issue_date")
CERTIFICATE_PREFIXES = {"income_certificate": "INC", "caste_certificate": "CST"}
KNOWN_TYPES = set(CERTIFICATE_PREFIXES) | {"marksheet", "identity_proof", "unknown"}
LABEL_KEYS = {
    "student name": "student_name",
    "certificate number": "certificate_number",
    "certificate no": "certificate_number",
    "certificate no.": "certificate_number",
    "application id": "application_id",
    "issue date": "issue_date",
}
LABEL_PATTERN = re.compile(
    r"[ \t]*(?P<label>Student[ \t]+Name|Certificate[ \t]+(?:Number|No\.?)|"
    r"Application[ \t]+ID|Issue[ \t]+Date)[ \t]*:[ \t]*(?P<value>.*?)[ \t]*",
    re.IGNORECASE | re.ASCII,
)
OBC_HOLDER_PATTERN = re.compile(
    r"\bthis is to certify that[ \t]+"
    r"(?P<name>[A-Za-z][A-Za-z .'-]{1,79}?)"
    r"[ \t]+(?:son\s*/\s*daughter|son|daughter)[ \t]+of\b",
    re.IGNORECASE | re.ASCII,
)
OBC_CERTIFICATE_NUMBER_PATTERN = re.compile(
    r"[ \t]*प्रमाण[ \t]*पत्र(?:[ \t]+(?:क्र|क)[०॰]?\.{0,2})?"
    r"[ \t]*:?[ \t]*(?P<value>[0-9]+)[ \t]*"
)
MISSING_MARKERS = {
    "", "unknown", "unreadable", "not found", "not found / unreadable",
    "not available", "none", "null", "n/a", "na", "missing",
}


def _validate_value(field, raw_value, doc_type):
    """Return a supported value or None, without repairing damaged characters."""
    value = raw_value.strip()
    if " ".join(value.casefold().split()) in MISSING_MARKERS:
        return None

    if field == "student_name":
        # These English demo names allow spaces, initials, apostrophes/hyphens.
        value = " ".join(value.split())
        if 2 <= len(value) <= 80 and re.fullmatch(
            r"[A-Za-z]+\.?(?:[ '-][A-Za-z]+\.?)*", value
        ):
            return value
        return None

    if field == "issue_date":
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            return None
        try:
            date.fromisoformat(value)  # Reject impossible days and non-leap Feb 29.
        except ValueError:
            return None
        return value

    prefix = "APP" if field == "application_id" else CERTIFICATE_PREFIXES[doc_type]
    # Bare numeric IDs or sample-specific prefixes followed by numeric groups.
    # Never cast to int: 00041 must remain 00041. Wrong prefixes are rejected.
    if len(value) <= 64 and re.fullmatch(
        rf"(?:[0-9]+|{prefix}-[0-9]+(?:-[0-9]+)*)",
        value, flags=re.IGNORECASE | re.ASCII,
    ):
        return value
    return None


def extract_fields(text, doc_type):
    """Return all four contract-v1 fields as strings or None.

    Known types allow name, application ID and ISO issue date. Only the two
    certificates allow a certificate number. Unknown types return all None,
    even if field labels are present. Unsupported type IDs and non-string
    inputs report caller errors explicitly.

    Repeated identical valid values are accepted. Conflicting values, or any
    malformed occurrence of the same supported label, leave that field None.
    Blank values never consume the next line. Unsupported layouts remain
    missing; absence, invalid text and ambiguity share None under contract v1.
    """
    if not isinstance(text, str):
        raise TypeError("extract_fields expects OCR text as a string.")
    if not isinstance(doc_type, str):
        raise TypeError("extract_fields expects doc_type as a string type ID.")
    if doc_type not in KNOWN_TYPES:
        raise ValueError(f"Unsupported document type: {doc_type!r}")

    fields = dict.fromkeys(FIELD_KEYS)
    if doc_type == "unknown":
        return fields

    candidates = {key: [] for key in FIELD_KEYS}
    for line in text.splitlines():
        match = LABEL_PATTERN.fullmatch(line)
        if match is None:
            continue
        label = " ".join(match.group("label").casefold().split())
        field = LABEL_KEYS[label]
        if field == "certificate_number" and doc_type not in CERTIFICATE_PREFIXES:
            continue
        candidates[field].append(_validate_value(field, match.group("value"), doc_type))

    if doc_type == "caste_certificate":
        normalized = " ".join(text.split())
        if OBC_CERTIFICATE_HEADING in normalized.casefold():
            for match in OBC_HOLDER_PATTERN.finditer(normalized):
                candidates["student_name"].append(
                    _validate_value("student_name", match.group("name"), doc_type)
                )
            for line in text.splitlines():
                if match := OBC_CERTIFICATE_NUMBER_PATTERN.fullmatch(line):
                    candidates["certificate_number"].append(
                        _validate_value("certificate_number", match.group("value"), doc_type)
                    )

    for field, values in candidates.items():
        if values and None not in values and len(set(values)) == 1:
            fields[field] = values[0]
    return fields
