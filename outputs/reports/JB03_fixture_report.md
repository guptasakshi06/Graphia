# Application readiness report

Demonstration scholarship checklist — FICTIONAL FIXTURE EXAMPLE, NOT REAL OCR

**Overall status: Needs Attention**

- Required document types: 4
- Submitted files: 6
- Detected required types (unique): 4
- Usable required types (unique): 3
- Document coverage: 100.00%
- Readiness: 75.00%
- Missing types: None
- Detected but unusable types: Identity Proof

## Selected configuration

Readability: selected OCR status must be ok, with at least 20 alphanumeric characters.

- Income Certificate: student\_name, certificate\_number
- Caste Certificate: student\_name, certificate\_number
- Marksheet: student\_name
- Identity Proof: student\_name

## Files

### FICTIONAL\_fixture-0.png

- Record ID: fixture-0
- Type: Income Certificate
- In selected checklist: Yes
- Classification evidence: income certificate
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 134
- Readable by heuristic: Yes
- Usable candidate: Yes
- Missing required fields: None
- student\_name: Asha Example
- certificate\_number: INC-00017
- application\_id: APP-00041
- issue\_date: 2026-01-15

Problems:

- None.

Selected OCR text:

```text
FICTIONAL REFERENCE ONLY - NOT REAL OCR
Income Certificate
Student Name: Asha Example
Application ID: APP-00041
Issue Date: 2026-01-15
Certificate Number: INC-00017
```

Processing settings:

```text
{
  "fixture_only": true
}
```

### FICTIONAL\_fixture-1.png

- Record ID: fixture-1
- Type: Caste Certificate
- In selected checklist: Yes
- Classification evidence: caste certificate
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 133
- Readable by heuristic: Yes
- Usable candidate: Yes
- Missing required fields: None
- student\_name: Asha Example
- certificate\_number: CST-00017
- application\_id: APP-00041
- issue\_date: 2026-01-15

Problems:

- None.

Selected OCR text:

```text
FICTIONAL REFERENCE ONLY - NOT REAL OCR
Caste Certificate
Student Name: Asha Example
Application ID: APP-00041
Issue Date: 2026-01-15
Certificate Number: CST-00017
```

Processing settings:

```text
{
  "fixture_only": true
}
```

### FICTIONAL\_fixture-2.png

- Record ID: fixture-2
- Type: Marksheet
- In selected checklist: Yes
- Classification evidence: marksheet
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 101
- Readable by heuristic: Yes
- Usable candidate: Yes
- Missing required fields: None
- student\_name: Asha Example
- certificate\_number: Not Found / Unreadable
- application\_id: APP-00041
- issue\_date: 2026-01-15

Problems:

- None.

Selected OCR text:

```text
FICTIONAL REFERENCE ONLY - NOT REAL OCR
Marksheet
Student Name: Asha Example
Application ID: APP-00041
Issue Date: 2026-01-15
```

Processing settings:

```text
{
  "fixture_only": true
}
```

### FICTIONAL\_fixture-3.png

- Record ID: fixture-3
- Type: Identity Proof
- In selected checklist: Yes
- Classification evidence: identity proof
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 77
- Readable by heuristic: Yes
- Usable candidate: No
- Missing required fields: student\_name
- student\_name: Not Found / Unreadable
- certificate\_number: Not Found / Unreadable
- application\_id: APP-00041
- issue\_date: Not Found / Unreadable

Problems:

- Missing required fields: student\_name.

Selected OCR text:

```text
FICTIONAL REFERENCE ONLY - NOT REAL OCR
Identity Proof
Student Name:
Application ID: APP-00041
```

Processing settings:

```text
{
  "fixture_only": true
}
```

### FICTIONAL\_fixture-bad-duplicate.png

- Record ID: fixture-bad-duplicate
- Type: Income Certificate
- In selected checklist: Yes
- Classification evidence: income certificate
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 60
- Readable by heuristic: Yes
- Usable candidate: No
- Missing required fields: student\_name, certificate\_number
- student\_name: Not Found / Unreadable
- certificate\_number: Not Found / Unreadable
- application\_id: Not Found / Unreadable
- issue\_date: Not Found / Unreadable

Problems:

- Missing required fields: student\_name, certificate\_number.

Selected OCR text:

```text
FICTIONAL REFERENCE ONLY - NOT REAL OCR
Income Certificate
Student Name:
```

Processing settings:

```text
{
  "fixture_only": true
}
```

### FICTIONAL\_fixture-unknown.png

- Record ID: fixture-unknown
- Type: Unknown Document
- In selected checklist: No
- Classification evidence: None
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 108
- Readable by heuristic: Yes
- Usable candidate: No
- Missing required fields: None
- student\_name: Not Found / Unreadable
- certificate\_number: Not Found / Unreadable
- application\_id: Not Found / Unreadable
- issue\_date: Not Found / Unreadable

Problems:

- Unknown document type; it cannot satisfy the checklist.

Selected OCR text:

```text
FICTIONAL REFERENCE ONLY - NOT REAL OCR
Unrelated receipt
Student Name: Asha Example
Application ID: APP-00041
Issue Date: 2026-01-15
```

Processing settings:

```text
{
  "fixture_only": true
}
```

## Limitations

- This demonstration checklist is fictional, not official scholarship policy.
- Readability is a heuristic: selected OCR status ok and the configured minimum alphanumeric character count. It does not prove OCR accuracy or human readability.
- Readiness checks configured presence and usable information only; it does not verify authenticity, official eligibility, or that documents belong to the same student.
- Each required type needs one individually usable file. Fields are never combined across files; duplicate types count once. OCR confidence is not accuracy.
