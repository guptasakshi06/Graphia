"""Conservative extraction for supported document layouts.

Most values follow a supported label on the same line. The supported OBC form
also identifies the holder in a certification sentence. Callers retain the
original OCR text separately.
"""

from datetime import date
import re

from modules.classification import (GRADE_SHEET_HEADING, HINDI_CASTE_HEADING, OBC_CERTIFICATE_HEADING,
                                    PAN_NUMBER, SC_CERTIFICATE_HEADING, find_pan_heading)


FIELD_KEYS = ("student_name", "certificate_number", "application_id", "issue_date")
DETAIL_LABELS = {
    "pan_number": "PAN number",
    "annual_income": "Annual income",
    "monthly_income": "Monthly income",
    "income_amount": "Income amount",
    "caste_category": "Caste category",
}
AMOUNT = r"(?:[0-9]{1,3}(?:,[0-9]{2})*,[0-9]{3}|[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]{1,2})?"
RUPEES = r"(?:₹|Rs\.?|INR|रु\.?|रू\.?|रुपये)"
INCOME_PERIODS = {
    "annual_income": r"(?:\b(?:annual|yearly)\s+(?:family\s+)?income\b|(?:वार्षिक|सालाना)\s*आय)",
    "monthly_income": r"(?:\bmonthly\s+(?:family\s+)?income\b|मासिक\s*आय)",
}
CASTE_CATEGORIES = {
    "SC": r"scheduled\s+caste(?:s)?|अनुसूचित\s+जाति|S\.?\s*C\.?",
    "ST": r"scheduled\s+tribe(?:s)?|अनुसूचित\s+जनजाति|S\.?\s*T\.?",
    "OBC": r"other\s+backward\s+class(?:es)?|अन्य\s+पिछड़ा\s+वर्ग|O\.?\s*B\.?\s*C\.?",
}
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
CERTIFICATION_HOLDER_PATTERN = re.compile(
    r"\bthis is to certify that[ \t]+(?:(?:shri|smt|mr|ms)\.?[ \t]+)?"
    r"(?P<name>[A-Za-z][A-Za-z .'-]{1,79}?)"
    r"[ \t]+(?:son\s*/\s*daughter|son|daughter)[ \t]+of\b",
    re.IGNORECASE | re.ASCII,
)
HINDI_CERTIFICATE_NUMBER_PATTERN = re.compile(
    r"[ \t]*प्रमाण[ \t-]*पत्र"
    r"(?:(?:[ \t]+(?:संख्या|(?:क्र|क|सं)[०॰]?\.{0,2}))?"
    r"[ \t]*:?[ \t]*(?P<value>[0-9]+)"
    # Accept a short OCR artifact only after the full label and before a colon.
    r"|[ \t]+[A-Za-z]{1,8}\.?[ \t]*:[ \t]*(?P<ocr_value>[0-9]{8,}))[ \t]*"
)
APPLICANT_NAME_PATTERN = re.compile(
    r"[ \t]*(?:[0-9]+\.[ \t]*)?"
    r"(?:(?:आवेदक|उम्मीदवार)[ \t]+का[ \t]+नाम(?:[ \t]*/[ \t]*Applicant[ \t]+Name)?"
    r"|Applicant[ \t]+Name)[ \t]*:[ \t]*(?P<value>.*?)[ \t]*",
    re.IGNORECASE,
)
MARKSHEET_CANDIDATE_PATTERN = re.compile(
    r"[ \t]*(?:Candidate[ '’]*s?[ \t]+Name|Name[ \t]+of[ \t]+(?:the[ \t]+)?Candidate"
    r"|उम्मीदवार[ \t]+का[ \t]+नाम)[ \t]*:[ \t]*(?P<value>.*?)[ \t]*",
    re.IGNORECASE,
)
PAN_NAME_PATTERN = re.compile(
    r"(?:नाम[ \t]*/[ \t]*)?Name(?:[ \t]*/[ \t]*नाम)?"
    r"(?:(?:[ \t]*:[ \t]*|[ \t]+)(?P<value>.*))?",
    re.IGNORECASE,
)
PAN_NON_NAME = re.compile(
    r"^(?:of|and)\b|\b(?:name|signature|date of birth|income tax department|government of india"
    r"|permanent account number|pan card)\b",
    re.IGNORECASE,
)
MISSING_MARKERS = {
    "", "unknown", "unreadable", "not found", "not found / unreadable",
    "not available", "none", "null", "n/a", "na", "missing",
}
HINDI_NAME_PATTERN = re.compile(r"[\u0904-\u0939\u0958-\u0961][\u0900-\u0963 '\-]+")


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


def _validate_holder(raw_value, doc_type):
    value = " ".join(raw_value.split())
    if 2 <= len(value) <= 80 and HINDI_NAME_PATTERN.fullmatch(value):
        return value
    return _validate_value("student_name", value, doc_type)


def extract_document_details(text, doc_type):
    """Return optional document-specific values separately from checklist fields."""
    if doc_type == "identity_proof" and find_pan_heading(text):
        numbers = set(PAN_NUMBER.findall(text.upper()))
        return {"pan_number": next(iter(numbers)) if len(numbers) == 1 else None}

    if doc_type == "income_certificate":
        normalized = " ".join(text.translate(str.maketrans("०१२३४५६७८९", "0123456789")).split())
        details = {}
        for key, label in INCOME_PERIODS.items():
            candidates = re.findall(
                rf"{label}\s*(?:(?:[:=]|is\b|of\b|से|लगभग|राशि)\s*|(?:from all sources|is assessed at)\s*)*"
                rf"(?:{RUPEES}\s*)?({AMOUNT})(?![\w,]|\.[0-9])",
                normalized, re.IGNORECASE,
            )
            if candidates:
                values = {value.replace(",", "") for value in candidates}
                details[key] = f"₹{next(iter(values))}" if len(values) == 1 else None
        if details:
            return details
        candidates = re.findall(
            rf"^\s*(?:total\s+)?income(?:\s+amount)?\s*[:=]\s*(?:{RUPEES}\s*)?({AMOUNT})(?![\w,]|\.[0-9])",
            text, re.IGNORECASE | re.MULTILINE,
        )
        values = {value.replace(",", "") for value in candidates}
        return {"income_amount": f"₹{next(iter(values))}" if len(values) == 1 else None}

    if doc_type == "caste_certificate":
        # Only use an explicit category label or certificate heading, not community names.
        normalized = " ".join(text.split())
        matches = set()
        if OBC_CERTIFICATE_HEADING in normalized.casefold():
            matches.add("OBC")
        if SC_CERTIFICATE_HEADING.search(text):
            matches.add("SC")
        for category, pattern in CASTE_CATEGORIES.items():
            if re.search(rf"(?<!\w)(?:{pattern})\s+(?:caste\s+)?certificate\b", normalized, re.IGNORECASE) or re.search(
                rf"^\s*(?:caste\s+category|category|श्रेणी|वर्ग)\s*[:=-]\s*(?:{pattern})(?!\w)",
                text, re.IGNORECASE | re.MULTILINE,
            ):
                matches.add(category)
        return {"caste_category": next(iter(matches)) if len(matches) == 1 else None}
    return {}


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

    normalized = " ".join(text.split())
    caste_layout = doc_type == "caste_certificate" and (
        HINDI_CASTE_HEADING.search(text)
        or any(heading in normalized.casefold() for heading in (
            OBC_CERTIFICATE_HEADING, "scheduled caste certificate", "form of caste certificate",
        ))
    )
    if doc_type == "income_certificate" or caste_layout:
        for match in CERTIFICATION_HOLDER_PATTERN.finditer(normalized):
            candidates["student_name"].append(
                _validate_value("student_name", match.group("name"), doc_type)
            )
        for line in text.splitlines():
            if match := HINDI_CERTIFICATE_NUMBER_PATTERN.fullmatch(line):
                candidates["certificate_number"].append(
                    _validate_value("certificate_number",
                                    match.group("value") or match.group("ocr_value"), doc_type)
                )
            if match := APPLICANT_NAME_PATTERN.fullmatch(line):
                candidates["student_name"].append(_validate_holder(match.group("value"), doc_type))

    if doc_type == "marksheet":
        for line in text.splitlines():
            match = MARKSHEET_CANDIDATE_PATTERN.fullmatch(line)
            if not match and GRADE_SHEET_HEADING.search(text):
                match = re.fullmatch(r"[ \t]*Name[ \t]*:[ \t]*(?P<value>.*?)\s*", line, re.IGNORECASE)
            if match:
                candidates["student_name"].append(_validate_holder(match.group("value"), doc_type))

    if doc_type == "identity_proof" and find_pan_heading(text):
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line, next_line in zip(lines, [*lines[1:], ""]):
            if match := PAN_NAME_PATTERN.fullmatch(line):
                value = match.group("value") or next_line
                candidates["student_name"].append(
                    None if PAN_NON_NAME.search(value) else _validate_holder(value, doc_type)
                )

    for field, values in candidates.items():
        if values and None not in values and len(set(values)) == 1:
            fields[field] = values[0]
    return fields
