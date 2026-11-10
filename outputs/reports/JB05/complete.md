# Application readiness report

Demonstration scholarship checklist

**Overall status: Ready**

- Required document types: 4
- Submitted files: 4
- Detected required types (unique): 4
- Usable required types (unique): 4
- Document coverage: 100.00%
- Readiness: 100.00%
- Missing types: None
- Detected but unusable types: None

## Selected configuration

Readability: selected OCR status must be ok, with at least 20 alphanumeric characters.

- Income Certificate: student\_name, certificate\_number
- Caste Certificate: student\_name, certificate\_number
- Marksheet: student\_name
- Identity Proof: student\_name

## Files

### income\_certificate\_clear.png

- Record ID: 0-a15f1e0deac4f32807b01e4e5463a3cb2ddf05b4abf8f523f77fc084db81e2c7
- Type: Income Certificate
- In selected checklist: Yes
- Classification evidence: income certificate
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 238
- Readable by heuristic: Yes
- Usable candidate: Yes
- Missing required fields: None
- student\_name: Asha Verma
- certificate\_number: INC-2026-0042
- application\_id: APP-2026-0101
- issue\_date: 2026-01-15

Problems:

- None.

Selected OCR text:

```text
SYNTHETIC SAMPLE - NOT AN OFFICIAL DOCUMENT
Income Certificate

Student Name: Asha Verma

Certificate Number: INC-2026-0042

Application ID: APP-2026-0101

Issue Date: 2026-01-15

Annual Family Income: INR 120000

Purpose: Classroom demonstration

Fictional classroom data. No official validity.

```

Processing settings:

```text
{
  "requested_options": {
    "denoise": "median",
    "kernel_size": 3,
    "contrast": "clahe",
    "threshold": "otsu",
    "global_threshold": 127,
    "adaptive_block_size": 31,
    "adaptive_c": 11.0,
    "morphology": "none",
    "morph_kernel_size": 2
  },
  "max_dimension": 1800,
  "loaded_dimensions": {
    "width": 1400,
    "height": 1000
  },
  "resolved_pipeline": {
    "denoise": "median",
    "kernel_size": 3,
    "contrast": "clahe",
    "threshold": "otsu",
    "global_threshold": 127,
    "adaptive_block_size": 31,
    "adaptive_c": 11.0,
    "morphology": "none",
    "morph_kernel_size": 2,
    "selected_otsu_threshold": 155.0,
    "clahe_clip_limit": 2.0,
    "clahe_tile_grid_size": [
      8,
      8
    ],
    "adaptive_method": "gaussian",
    "morph_kernel_shape": "rectangle",
    "morph_iterations": 1,
    "morph_anchor_xy": [
      1,
      1
    ],
    "morph_border": "constant neutral (erosion=255, dilation=0)",
    "morph_foreground": "inverted white text; restored after operation",
    "output_polarity": "dark text / light background (input convention)",
    "input_shape": [
      1000,
      1400,
      3
    ],
    "output_shape": [
      1000,
      1400
    ]
  }
}
```

### caste\_certificate\_clear.png

- Record ID: 1-2dcfc270cf2ada44313d8c4d7712af16949a4181aa702039828c255bb13250db
- Type: Caste Certificate
- In selected checklist: Yes
- Classification evidence: caste certificate
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 246
- Readable by heuristic: Yes
- Usable candidate: Yes
- Missing required fields: None
- student\_name: Neel Rao
- certificate\_number: CST-2026-0043
- application\_id: APP-2026-0102
- issue\_date: 2026-01-16

Problems:

- None.

Selected OCR text:

```text
SYNTHETIC SAMPLE - NOT AN OFFICIAL DOCUMENT
Caste Certificate

Student Name: Neel Rao

Certificate Number: CST-2026-0043

Application ID: APP-2026-0102

Issue Date: 2026-01-16

Category: Fictional demonstration category
Purpose: Classroom demonstration

Fictional classroom data. No official validity.

```

Processing settings:

```text
{
  "requested_options": {
    "denoise": "median",
    "kernel_size": 3,
    "contrast": "clahe",
    "threshold": "otsu",
    "global_threshold": 127,
    "adaptive_block_size": 31,
    "adaptive_c": 11.0,
    "morphology": "none",
    "morph_kernel_size": 2
  },
  "max_dimension": 1800,
  "loaded_dimensions": {
    "width": 1400,
    "height": 1000
  },
  "resolved_pipeline": {
    "denoise": "median",
    "kernel_size": 3,
    "contrast": "clahe",
    "threshold": "otsu",
    "global_threshold": 127,
    "adaptive_block_size": 31,
    "adaptive_c": 11.0,
    "morphology": "none",
    "morph_kernel_size": 2,
    "selected_otsu_threshold": 155.0,
    "clahe_clip_limit": 2.0,
    "clahe_tile_grid_size": [
      8,
      8
    ],
    "adaptive_method": "gaussian",
    "morph_kernel_shape": "rectangle",
    "morph_iterations": 1,
    "morph_anchor_xy": [
      1,
      1
    ],
    "morph_border": "constant neutral (erosion=255, dilation=0)",
    "morph_foreground": "inverted white text; restored after operation",
    "output_polarity": "dark text / light background (input convention)",
    "input_shape": [
      1000,
      1400,
      3
    ],
    "output_shape": [
      1000,
      1400
    ]
  }
}
```

### marksheet\_clear.png

- Record ID: 2-0be87a714356c1aec8e1ca42542ca1f894c9d3faac0f1035bdbd8aaf90f80548
- Type: Marksheet
- In selected checklist: Yes
- Classification evidence: marksheet
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 215
- Readable by heuristic: Yes
- Usable candidate: Yes
- Missing required fields: None
- student\_name: Mira Sen
- certificate\_number: Not Found / Unreadable
- application\_id: APP-2026-0103
- issue\_date: 2026-01-17

Problems:

- None.

Selected OCR text:

```text
SYNTHETIC SAMPLE - NOT AN OFFICIAL DOCUMENT
Marksheet

Student Name: Mira Sen

Application ID: APP-2026-0103

Issue Date: 2026-01-17

Examination: Sample Semester

Mathematics: 81 / 100

Computer Science: 87 / 100

Result: Pass

Fictional classroom data. No official validity.

```

Processing settings:

```text
{
  "requested_options": {
    "denoise": "median",
    "kernel_size": 3,
    "contrast": "clahe",
    "threshold": "otsu",
    "global_threshold": 127,
    "adaptive_block_size": 31,
    "adaptive_c": 11.0,
    "morphology": "none",
    "morph_kernel_size": 2
  },
  "max_dimension": 1800,
  "loaded_dimensions": {
    "width": 1400,
    "height": 1000
  },
  "resolved_pipeline": {
    "denoise": "median",
    "kernel_size": 3,
    "contrast": "clahe",
    "threshold": "otsu",
    "global_threshold": 127,
    "adaptive_block_size": 31,
    "adaptive_c": 11.0,
    "morphology": "none",
    "morph_kernel_size": 2,
    "selected_otsu_threshold": 156.0,
    "clahe_clip_limit": 2.0,
    "clahe_tile_grid_size": [
      8,
      8
    ],
    "adaptive_method": "gaussian",
    "morph_kernel_shape": "rectangle",
    "morph_iterations": 1,
    "morph_anchor_xy": [
      1,
      1
    ],
    "morph_border": "constant neutral (erosion=255, dilation=0)",
    "morph_foreground": "inverted white text; restored after operation",
    "output_polarity": "dark text / light background (input convention)",
    "input_shape": [
      1000,
      1400,
      3
    ],
    "output_shape": [
      1000,
      1400
    ]
  }
}
```

### identity\_proof\_clear.png

- Record ID: 3-4d4aa7e871816b5ac919473dd26b4d22851653d3078ffafad7c98d749559b0aa
- Type: Identity Proof
- In selected checklist: Yes
- Classification evidence: identity proof
- Ambiguous classification: No
- Selected OCR source: processed
- Selected OCR status: ok
- Alphanumeric characters: 199
- Readable by heuristic: Yes
- Usable candidate: Yes
- Missing required fields: None
- student\_name: Dev Mehta
- certificate\_number: Not Found / Unreadable
- application\_id: APP-2026-0104
- issue\_date: 2026-01-18

Problems:

- None.

Selected OCR text:

```text
SYNTHETIC SAMPLE - NOT AN OFFICIAL DOCUMENT
Identity Proof

Student Name: Dev Mehta

Application ID: APP-2026-0104

Issue Date: 2026-01-18

Institution: Example Learning Centre

Student ID: DEMO-042-04

Fictional classroom data. No official validity.

```

Processing settings:

```text
{
  "requested_options": {
    "denoise": "median",
    "kernel_size": 3,
    "contrast": "clahe",
    "threshold": "otsu",
    "global_threshold": 127,
    "adaptive_block_size": 31,
    "adaptive_c": 11.0,
    "morphology": "none",
    "morph_kernel_size": 2
  },
  "max_dimension": 1800,
  "loaded_dimensions": {
    "width": 1400,
    "height": 1000
  },
  "resolved_pipeline": {
    "denoise": "median",
    "kernel_size": 3,
    "contrast": "clahe",
    "threshold": "otsu",
    "global_threshold": 127,
    "adaptive_block_size": 31,
    "adaptive_c": 11.0,
    "morphology": "none",
    "morph_kernel_size": 2,
    "selected_otsu_threshold": 156.0,
    "clahe_clip_limit": 2.0,
    "clahe_tile_grid_size": [
      8,
      8
    ],
    "adaptive_method": "gaussian",
    "morph_kernel_shape": "rectangle",
    "morph_iterations": 1,
    "morph_anchor_xy": [
      1,
      1
    ],
    "morph_border": "constant neutral (erosion=255, dilation=0)",
    "morph_foreground": "inverted white text; restored after operation",
    "output_polarity": "dark text / light background (input convention)",
    "input_shape": [
      1000,
      1400,
      3
    ],
    "output_shape": [
      1000,
      1400
    ]
  }
}
```

## Limitations

- This demonstration checklist is fictional, not official scholarship policy.
- Readability is a heuristic: selected OCR status ok and the configured minimum alphanumeric character count. It does not prove OCR accuracy or human readability.
- Readiness checks configured presence and usable information only; it does not verify authenticity, official eligibility, or that documents belong to the same student.
- Each required type needs one individually usable file. Fields are never combined across files; duplicate types count once. OCR confidence is not accuracy.
