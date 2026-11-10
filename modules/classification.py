"""Small, conservative rules for supported document titles.

Input is OCR text, never a filename. Matching uses a temporary normalized copy;
callers must retain the original OCR text for display and later extraction.
No image, OCR engine, Streamlit, or third-party package is required here.
"""

import re


OBC_CERTIFICATE_HEADING = "form of certificate to be produced by other backward classes"
PAN_CARD_HEADING = re.compile(
    r"^[ \t]*(?P<title>permanent\s+account\s+number\s+card|pan\s+card)[ \t]*\r?$",
    re.IGNORECASE | re.MULTILINE,
)
HINDI_INCOME_HEADING = re.compile(
    r"^[ \t]*(?:कार्यालय[ \t]+तहसीलदार[ \t]+द्वारा[ \t]+प्रदत्त[ \t]+)?"
    r"(?P<title>आय[ \t]+प्रमाण[ \t-]*पत्र)[ \t।]*\r?$",
    re.MULTILINE,
)
DOCUMENT_HEADINGS = {
    "income_certificate": HINDI_INCOME_HEADING,
    "identity_proof": PAN_CARD_HEADING,
}

# Keep order fixed so evidence and test results are reproducible.
TITLE_KEYWORDS = {
    "income_certificate": ("income certificate",),
    "caste_certificate": ("caste certificate", OBC_CERTIFICATE_HEADING),
    "marksheet": ("marksheet", "mark sheet"),
    "identity_proof": ("identity proof",),
}


def classify_document(text):
    """Return contract-v1 type, matched phrases, and competing-type ambiguity.

    Case and whitespace differences are ignored. Whole phrases must match:
    'income' alone is insufficient, and 'marksheet' inside a longer word does
    not count. Two distinct matching types yield unknown, regardless of how
    often either title occurs. Evidence is normalized vocabulary, not a score
    or confidence percentage. Blank/unrelated strings safely yield unknown.

    Non-string inputs raise TypeError so upstream programming errors remain
    visible instead of being silently turned into unknown documents.
    """
    if not isinstance(text, str):
        raise TypeError("classify_document expects OCR text as a string.")

    normalized = " ".join(text.casefold().split())
    matched_types = []
    evidence = []
    for doc_type, keywords in TITLE_KEYWORDS.items():
        matches = [
            keyword for keyword in keywords
            if re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", normalized)
        ]
        heading_pattern = DOCUMENT_HEADINGS.get(doc_type)
        if heading_pattern and (heading := heading_pattern.search(text)):
            matches.append(" ".join(heading.group("title").casefold().split()))
        if matches:
            matched_types.append(doc_type)
            evidence.extend(matches)

    return {
        "doc_type": matched_types[0] if len(matched_types) == 1 else "unknown",
        "evidence": evidence,
        "ambiguous": len(matched_types) > 1,
    }
