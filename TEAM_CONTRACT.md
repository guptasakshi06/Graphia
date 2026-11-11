# Shared interfaces — Project 042

**Version:** 1, frozen at M00 on 2026-11-10. **Owner:** integration chat. This is an API specification, not implemented application code. Changes after M00 must be coordinated at an M gate and documented with caller updates.

Read the master handoff's behavior rules as well. Use ordinary Python functions/dictionaries; no service layer or elaborate schema framework is needed.

## 1. Constants and sample vocabulary

- Document types: `income_certificate`, `caste_certificate`, `marksheet`, `identity_proof`, `unknown`.
- Field keys: `student_name`, `certificate_number`, `application_id`, `issue_date`.
- Demonstration labels: `Student Name:`, `Certificate Number:`, `Application ID:`, `Issue Date:`. Support conservative label variants when observed; do not require every label on every type.
- Sample title cues: Income Certificate, Caste Certificate, Marksheet, Identity Proof. Never classify by filename.
- Baseline fixture requirement: name on all four types, certificate number on the two certificates. Other fields are extracted where present but optional by default. These are made-up demonstration layouts/requirements, not official forms.
- Dates in generated fixtures: ISO `YYYY-MM-DD` for reproducibility. Extra formats may be supported only with explained unambiguous parsing.
- Fixture text and expected fields may be created before real OCR exists, but must be labeled reference/test text. Final tests must also use actual OCR outputs.

## 2. Image APIs — Sakshi owns implementation

```python
load_image(source, max_dimension=1800)
run_pipeline(image_bgr, options=None)
extract_text(image, lang="eng", psm=6, timeout=20)
```

`load_image` is exported from `modules.preprocessing`. `source` accepts a path (`str`/`Path`) or encoded image `bytes`; UI uses `uploaded_file.getvalue()`. Return a BGR `uint8` array with aspect ratio preserved, EXIF orientation applied and transparency composited on white. Invalid inputs raise a clear `ValueError`. Do not mutate input arrays in later processing. The 1800-pixel maximum is a documented initial limit, adjustable only with evidence.

`run_pipeline`, also from `modules.preprocessing`, accepts BGR input and a plain options dict. Return:

```text
{
  "stages": {
    "original": BGR array,
    "grayscale": gray array,
    "denoised": gray array,
    "enhanced": gray array,
    "thresholded": gray/binary array,
    "morphology": gray/binary array
  },
  "ocr_input": gray/binary array,
  "parameters": JSON-serializable resolved settings
}
```

When an optional stage is bypassed, its named image remains available as an unchanged copy of the preceding stage. `ocr_input` defaults to the final selected stage; morphology must restore dark-text/light-background polarity for OCR. Display-only conversion to RGB belongs in the UI or plotting code, never by guessing channel order downstream.

Initial public options (all defaults recorded in parameters):

| Key | Values | Initial default |
|---|---|---|
| `denoise` | `none`, `gaussian`, `median` | `median` |
| `kernel_size` | positive odd integer | `3` |
| `contrast` | `none`, `equalize`, `clahe` | `clahe` |
| `threshold` | `none`, `global`, `otsu`, `adaptive` | `otsu` |
| `global_threshold` | integer 0–255 | `127` |
| `adaptive_block_size` | odd integer greater than 1 | `31` |
| `adaptive_c` | numeric | `11` |
| `morphology` | `none`, `erosion`, `dilation`, `opening`, `closing` | `none` |
| `morph_kernel_size` | positive integer | `2` |

These are fixed contract-v1 starting defaults, not a claim of OCR optimality. Any change to public defaults must be recorded at a merge gate; per-call option overrides remain supported. Sakshi records actual CLAHE settings and any chosen changes; Jigisha reads resolved settings instead of maintaining a separate hidden pipeline. Invalid option names/values fail clearly. Helpers for individual operations may be added without changing these exported APIs.

`extract_text` is exported from `modules.ocr`. Accept either BGR or grayscale `uint8` arrays; normalize color correctly before passing to Pytesseract. Return:

```text
{
  "text": string,
  "status": "ok" | "no_text" | "error",
  "confidence": number | null,
  "error": string | null,
  "engine_config": {"lang": string, "psm": integer, "timeout": number}
}
```

For missing Tesseract/language data, timeout or OCR failure return `status: error` and a meaningful error; do not hide a setup error as no text. `no_text` means the engine ran but no usable text was obtained. Confidence is an optional heuristic, never an accuracy percentage. No UI imports in these modules.

## 3. Text APIs — Jigisha owns implementation

```python
classify_document(text)
extract_fields(text, doc_type)
```

`classify_document` in `modules.classification` returns:

```text
{"doc_type": type ID, "evidence": [matched keyword strings], "ambiguous": boolean}
```

Blank/unrelated text is `unknown`; conflicting competing class evidence is conservatively `unknown` with `ambiguous: true`. Keep raw OCR for display. Matching normalization must not modify the stored original.

`extract_fields` in `modules.extraction` returns a dict containing all four field keys with string values or `None`. No fabricated fallback value; no automatic choice of any arbitrary number/date. Format missing values only in the UI/report as `Not Found / Unreadable`. Do not require not-applicable fields for readiness. Additional metadata may be added in a coordinated contract revision if needed.

Post-M03 extension: an optional `document_details` mapping carries document-specific string or `None` values (`pan_number`, `annual_income`, `monthly_income`, `income_amount`, `caste_category`). The UI and exports display it when present. It does not change the four checklist fields or readiness rules. A grade sheet's holder remains `student_name`.

## 4. Configuration, document record and readiness — Jigisha owns implementation

`config/requirements.json` shape:

```json
{
  "profile_name": "Demonstration scholarship checklist",
  "required_documents": {
    "income_certificate": ["student_name", "certificate_number"],
    "caste_certificate": ["student_name", "certificate_number"],
    "marksheet": ["student_name"],
    "identity_proof": ["student_name"]
  },
  "readability": {"min_alnum_chars": 20}
}
```

This is the planned default. Validate unknown types, invalid field names, nonpositive readability settings and malformed/empty configurations. Users can select a nonempty subset of required types in the UI; do not allow `unknown` as a required type. Do not describe this as an official scholarship policy.

The UI builds per-document records:

```text
{
  "id": stable unique string,
  "filename": string,
  "ocr_original": OCR result,
  "ocr_processed": OCR result,
  "ocr_source": "original" | "processed",
  "ocr": selected OCR result,
  "classification": classification result from selected OCR text,
  "fields": extracted field dict from the same selected OCR text/type,
  "processing_parameters": JSON-serializable settings
}
```

Keep image arrays outside serializable reports. Default selection is processed OCR, but allow original selection when processing damages text. Recalculate classification/fields when selection changes. A same-name upload must not overwrite another record; use an index/hash-based stable ID. Unknown/corrupt files remain visible, with clear status rather than silently disappearing.

```python
analyze_readiness(records, config, required_types=None)
render_report(report)
```

Both functions live in `modules.readiness`. `required_types=None` means configured types; an explicitly empty list is a validation error. `analyze_readiness` returns JSON-serializable data with at least:

```text
profile_name, required_types, required_type_count,
submitted_file_count, detected_required_type_count, usable_required_type_count,
missing_types, unusable_types, coverage_percent, readiness_percent,
overall_status, documents, limitations
```

`documents` retains each file's OCR/fields/type and per-file readable flag, missing required field list and problems. `unusable_types` means detected required types with no individually usable candidate. An unknown item is not a detected required type.

Readability's initial heuristic is selected OCR status `ok` and at least the configured count of alphanumeric characters (`str.isalnum`). This is an explicit heuristic, not correctness, authenticity or human readability proof. A candidate is usable only when readable **and** all configured required fields for its type are nonempty. Each type needs one complete candidate; do not combine fields across files. Duplicate types count once.

- Coverage = `100 * detected_required_type_count / required_type_count`.
- Readiness = `100 * usable_required_type_count / required_type_count`.
- Overall status: `Incomplete` if any required type is absent; otherwise `Needs Attention` if any detected required type has no usable candidate; otherwise `Ready`.
- Preserve raw precision for calculations; round only for display.
- `render_report` returns readable Markdown/text including counts, percentages, selected configuration, files/fields, problems and the authenticity/eligibility limitation. Use `json.dumps` for structured downloads.

## 5. Integration and development adapters

Jigisha can use fixtures and a small test-only fake provider while Sakshi builds image/OCR modules. Keep it under her tests or a clearly labeled development-only path; never add fake results as a production fallback. Her UI may delay image/OCR imports until the analyze action with a clear `Awaiting real DIP/OCR modules` message. Do not create competing `modules/preprocessing.py` or `modules/ocr.py` implementations.

At M01 remove/disable development adapters in the production path, import these exact functions, and run a real sample through every module. Readiness and extraction results must use the same selected OCR result. Neither person can claim the complete application works before this gate.

After M01, both tracks test from the merged code. At M02 freeze actual evidence before writing final report/slides. At M03 combine their separate documents and viva sources without changing measured values.

## M00 API freeze record — 2026-11-10

Validated the five application module owners and all public functions, document/field IDs, options, result keys, configuration and readiness formulas. No signature or schema changes were needed. The option table fixes caller defaults; later experiments may recommend explicit overrides. `modules/__init__.py` is only a package marker. No application implementation or human review is implied by this freeze. Any incompatible change requires a versioned merge-gate record and updates to both producers and callers.
