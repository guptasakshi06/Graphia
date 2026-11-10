"""Contract-v1 checklist checks and Markdown exports, independent of OCR/UI.

Callers classify/extract from the same selected OCR result. This module checks
that each required type has one complete usable candidate, never pooled fields.
Only serializable record data enters reports; images belong outside records.
"""

from copy import deepcopy
import json
import math

from modules.classification import TITLE_KEYWORDS
from modules.extraction import FIELD_KEYS


TYPE_NAMES = {
    "income_certificate": "Income Certificate",
    "caste_certificate": "Caste Certificate",
    "marksheet": "Marksheet",
    "identity_proof": "Identity Proof",
    "unknown": "Unknown Document",
}
LIMITATIONS = [
    "This demonstration checklist is fictional, not official scholarship policy.",
    "Readability is a heuristic: selected OCR status ok and the configured minimum "
    "alphanumeric character count. It does not prove OCR accuracy or human readability.",
    "Readiness checks configured presence and usable information only; it does not "
    "verify authenticity, official eligibility, or that documents belong to the same student.",
    "Each required type needs one individually usable file. Fields are never combined "
    "across files; duplicate types count once. OCR confidence is not accuracy.",
]
RECORD_KEYS = (
    "id", "filename", "ocr_original", "ocr_processed", "ocr_source", "ocr",
    "classification", "fields", "processing_parameters",
)


def _validate_config(config, required_types):
    """Reject malformed policies; return a nonempty selection in caller order."""
    if not isinstance(config, dict) or set(config) != {
        "profile_name", "required_documents", "readability"
    }:
        raise ValueError("Config needs profile_name, required_documents and readability only.")
    if not isinstance(config["profile_name"], str) or not config["profile_name"].strip():
        raise ValueError("Config profile_name must be a nonempty string.")
    requirements = config["required_documents"]
    if not isinstance(requirements, dict) or not requirements:
        raise ValueError("required_documents must be a nonempty mapping.")
    for doc_type, fields in requirements.items():
        if doc_type not in TITLE_KEYWORDS:
            raise ValueError(f"Invalid required document type: {doc_type!r}")
        if (not isinstance(fields, list)
                or any(not isinstance(field, str) or field not in FIELD_KEYS for field in fields)
                or len(fields) != len(set(fields))):
            raise ValueError(f"Required fields for {doc_type} must be a list of unique field IDs.")
    readability = config["readability"]
    if not isinstance(readability, dict) or set(readability) != {"min_alnum_chars"}:
        raise ValueError("readability needs min_alnum_chars only.")
    minimum = readability["min_alnum_chars"]
    if type(minimum) is not int or minimum <= 0:
        raise ValueError("min_alnum_chars must be a positive integer.")
    selected = list(requirements) if required_types is None else required_types
    if (not isinstance(selected, (list, tuple)) or not selected
            or any(not isinstance(item, str) or item not in requirements for item in selected)
            or len(selected) != len(set(selected))):
        raise ValueError("required_types must be a nonempty, unique list of configured type IDs.")
    return list(selected)


def _validate_ocr(ocr):
    """Keep setup failures distinct from successful OCR with no text."""
    if not isinstance(ocr, dict) or not {
        "text", "status", "confidence", "error", "engine_config"
    }.issubset(ocr):
        raise ValueError("Each OCR result needs the five contract-v1 OCR keys.")
    if not isinstance(ocr["text"], str) or ocr["status"] not in ("ok", "no_text", "error"):
        raise ValueError("OCR needs string text and status ok, no_text or error.")
    confidence = ocr["confidence"]
    if confidence is not None and (
        type(confidence) not in (int, float) or not math.isfinite(confidence)
    ):
        raise ValueError("OCR confidence must be a finite number or None.")
    if ocr["error"] is not None and not isinstance(ocr["error"], str):
        raise ValueError("OCR error must be a string or None.")
    if ocr["status"] == "error" and not ocr["error"]:
        raise ValueError("OCR error status needs an explanation.")
    if not isinstance(ocr["engine_config"], dict) or not {
        "lang", "psm", "timeout"
    }.issubset(ocr["engine_config"]):
        raise ValueError("OCR engine_config needs lang, psm and timeout.")


def _copy_record(record, seen_ids):
    """Validate boundary data and copy public record keys without image arrays."""
    if not isinstance(record, dict) or not set(RECORD_KEYS).issubset(record):
        raise ValueError("Document record is missing contract-v1 keys.")
    for key in ("id", "filename"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValueError(f"Record {key} must be a nonempty string.")
    if record["id"] in seen_ids:
        raise ValueError(f"Duplicate record ID: {record['id']!r}; use distinct IDs for uploads.")
    seen_ids.add(record["id"])
    for key in ("ocr_original", "ocr_processed", "ocr"):
        _validate_ocr(record[key])
    source = record["ocr_source"]
    if source not in ("original", "processed") or record["ocr"] != record["ocr_" + source]:
        raise ValueError("ocr must equal the result named by ocr_source (original or processed).")
    classification = record["classification"]
    if not isinstance(classification, dict) or not {
        "doc_type", "evidence", "ambiguous"
    }.issubset(classification):
        raise ValueError("Classification is missing contract-v1 keys.")
    if (not isinstance(classification["doc_type"], str)
            or classification["doc_type"] not in TYPE_NAMES
            or not isinstance(classification["evidence"], list)
            or not all(isinstance(item, str) for item in classification["evidence"])
            or type(classification["ambiguous"]) is not bool
            or (classification["ambiguous"] and classification["doc_type"] != "unknown")):
        raise ValueError("Invalid classification type, evidence or ambiguity.")
    fields = record["fields"]
    if (not isinstance(fields, dict) or set(fields) != set(FIELD_KEYS)
            or not all(value is None or isinstance(value, str) for value in fields.values())):
        raise ValueError("fields must contain all four string/None values.")
    if not isinstance(record["processing_parameters"], dict):
        raise ValueError("processing_parameters must be a JSON-serializable dictionary.")
    copied = {key: deepcopy(record[key]) for key in RECORD_KEYS}
    try:
        json.dumps(copied, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("Record report data must be JSON serializable without images/NaN.") from error
    return copied


def analyze_readiness(records, config, required_types=None):
    """Return serializable per-file checks and unique-type application totals.

    Empty uploads are valid and Incomplete. Empty selections are invalid.
    Configured per-type field lists may be empty to explicitly require no fields.
    Whitespace-only fields are missing. The readability threshold uses str.isalnum
    (including Unicode letters/digits), not confidence, length or punctuation.
    Caller data is never mutated. Malformed input raises ValueError.
    """
    selected = _validate_config(config, required_types)
    if not isinstance(records, (list, tuple)):
        raise ValueError("records must be a list or tuple of document records.")
    minimum = config["readability"]["min_alnum_chars"]
    documents, seen_ids, detected, usable = [], set(), set(), set()
    for record in records:
        document = _copy_record(record, seen_ids)
        doc_type = document["classification"]["doc_type"]
        ocr = document["ocr"]
        alnum_count = sum(character.isalnum() for character in ocr["text"])
        readable = ocr["status"] == "ok" and alnum_count >= minimum
        fields_needed = config["required_documents"].get(doc_type, [])
        missing_fields = [field for field in fields_needed if not (document["fields"][field] or "").strip()]
        candidate_usable = doc_type != "unknown" and readable and not missing_fields
        problems = []
        if doc_type == "unknown":
            problems.append("Unknown document type; it cannot satisfy the checklist.")
        elif doc_type not in selected:
            problems.append("Document type is not in the selected checklist.")
        if document["classification"]["ambiguous"]:
            problems.append("Conflicting document-title evidence; classification is ambiguous.")
        if ocr["status"] == "error":
            problems.append("OCR error: " + ocr["error"])
        elif ocr["status"] == "no_text":
            problems.append("OCR completed with no usable text.")
        if alnum_count < minimum:
            problems.append(f"Only {alnum_count} alphanumeric characters; minimum is {minimum}.")
        if missing_fields:
            problems.append("Missing required fields: " + ", ".join(missing_fields) + ".")
        document.update({
            "doc_type": doc_type, "is_required": doc_type in selected,
            "alnum_char_count": alnum_count, "readable": readable,
            "required_fields": list(fields_needed), "missing_required_fields": missing_fields,
            "usable": candidate_usable, "problems": problems,
        })
        documents.append(document)
        if doc_type in selected:
            detected.add(doc_type)
            if candidate_usable:
                usable.add(doc_type)

    missing_types = [doc_type for doc_type in selected if doc_type not in detected]
    unusable_types = [doc_type for doc_type in selected if doc_type in detected - usable]
    return {
        "profile_name": config["profile_name"], "configuration": deepcopy(config),
        "required_types": selected, "required_type_count": len(selected),
        "submitted_file_count": len(documents),
        "detected_required_type_count": len(detected), "usable_required_type_count": len(usable),
        "missing_types": missing_types, "unusable_types": unusable_types,
        "coverage_percent": 100 * len(detected) / len(selected),
        "readiness_percent": 100 * len(usable) / len(selected),
        "overall_status": "Incomplete" if missing_types else "Needs Attention" if unusable_types else "Ready",
        "documents": documents, "limitations": list(LIMITATIONS),
    }


def _markdown(value):
    """Escape inline OCR/filename content so it stays text in a Markdown report."""
    value = str(value).replace("\\", "\\\\")
    for character in "`*_{}[]<>()#+!|":
        value = value.replace(character, "\\" + character)
    return value.replace("\r", " ").replace("\n", " ")


def _text_block(text):
    """Use a fence longer than any run of backticks in untrusted OCR text."""
    longest = 0
    # Count runs directly; arbitrary OCR may itself contain Markdown fences.
    run = 0
    for character in text:
        run = run + 1 if character == "`" else 0
        longest = max(longest, run)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def render_report(report):
    """Render an analyze_readiness result as downloadable Markdown (no writes)."""
    def names(type_ids):
        return ", ".join(TYPE_NAMES[item] for item in type_ids) or "None"

    lines = [
        "# Application readiness report", "", _markdown(report["profile_name"]), "",
        f"**Overall status: {report['overall_status']}**", "",
        f"- Required document types: {report['required_type_count']}",
        f"- Submitted files: {report['submitted_file_count']}",
        f"- Detected required types (unique): {report['detected_required_type_count']}",
        f"- Usable required types (unique): {report['usable_required_type_count']}",
        f"- Document coverage: {report['coverage_percent']:.2f}%",
        f"- Readiness: {report['readiness_percent']:.2f}%",
        f"- Missing types: {names(report['missing_types'])}",
        f"- Detected but unusable types: {names(report['unusable_types'])}", "",
        "## Selected configuration", "",
        "Readability: selected OCR status must be ok, with at least "
        f"{report['configuration']['readability']['min_alnum_chars']} alphanumeric characters.", "",
    ]
    for doc_type in report["required_types"]:
        fields = report["configuration"]["required_documents"][doc_type]
        lines.append(f"- {TYPE_NAMES[doc_type]}: " + _markdown(", ".join(fields) or "no required fields"))
    lines.extend(["", "## Files", ""])
    if not report["documents"]:
        lines.extend(["No files submitted.", ""])
    for document in report["documents"]:
        lines.extend([
            "### " + _markdown(document["filename"]), "",
            "- Record ID: " + _markdown(document["id"]),
            "- Type: " + TYPE_NAMES[document["doc_type"]],
            f"- In selected checklist: {'Yes' if document['is_required'] else 'No'}",
            "- Classification evidence: " + _markdown(", ".join(document["classification"]["evidence"]) or "None"),
            f"- Ambiguous classification: {'Yes' if document['classification']['ambiguous'] else 'No'}",
            "- Selected OCR source: " + document["ocr_source"],
            "- Selected OCR status: " + document["ocr"]["status"],
            f"- Alphanumeric characters: {document['alnum_char_count']}",
            f"- Readable by heuristic: {'Yes' if document['readable'] else 'No'}",
            f"- Usable candidate: {'Yes' if document['usable'] else 'No'}",
            "- Missing required fields: " + _markdown(", ".join(document["missing_required_fields"]) or "None"),
        ])
        for field in FIELD_KEYS:
            value = document["fields"][field]
            lines.append(f"- {_markdown(field)}: " + _markdown(value if value and value.strip() else "Not Found / Unreadable"))
        lines.extend(["", "Problems:", ""])
        lines.extend("- " + _markdown(problem) for problem in document["problems"] or ["None."])
        lines.extend(["", "Selected OCR text:", "", _text_block(document["ocr"]["text"]), "",
                      "Processing settings:", "", _text_block(json.dumps(
                          document["processing_parameters"], ensure_ascii=False, indent=2, allow_nan=False)), ""])
    lines.extend(["## Limitations", ""])
    lines.extend("- " + _markdown(limitation) for limitation in report["limitations"])
    return "\n".join(lines) + "\n"
