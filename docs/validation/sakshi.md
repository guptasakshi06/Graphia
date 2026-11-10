# SG05 — Sakshi's final integrated measurements

Measured 2026-11-10 15:08 Asia/Kolkata. SG05 evidence candidate for **M02**, not yet merged
or frozen. Browser scenarios/screenshots belong to JB05. This summary records
real local execution; no student/human review, general accuracy or official
eligibility is claimed.

## Code, data and measurement boundary

- Checkout: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi`;
  branch `codex/sakshi-dip`; M01 baseline `183ff6bfa6e67e2156eafc282044eb151e07ad39`.
  Clean start; fast-forward synchronization reported already up to date.
- `metrics.json` fingerprints all production modules, app, configuration,
  contract and both experiment scripts. No production code, configuration,
  dependency or public default changed in SG05.
- Eight project-created fictional PNGs; four distinct layouts and four related
  degraded derivatives. Clear (4), low contrast (1), Gaussian noise (1), slight
  blur (2). These are not eight independent real-world documents.
- `dataset/manifest.json` contains expected types, fields, raw transcripts,
  provenance and degradation settings. Every image/reference hash was rechecked
  against `dataset/visual_review.json` (SG01 assistant inspection). Existing
  contact sheet was opened again and compared against the four distinct raw
  transcripts. No new student/human verification is claimed.
- All images load at 1400×1000 BGR uint8; the 1800-pixel limit does not resize
  these samples. Original arrays remain unchanged.
- Tesseract 5.3.4, Pytesseract 0.3.13,
  English, PSM 6, 20-second timeout. Confidence remains null, never accuracy.
- **112 real OCR calls**: 8 samples × 14 methods. A separate **16 real calls**
  run all eight upload byte payloads through the unchanged `app.analyze_uploads`
  and `app.load_real_provider`. That exercises image → DIP → original/processed
  OCR → real classification/extraction → readiness. No fixture provider.

## All seven comparison groups and fixed settings

| Required comparison | Methods | Figure in each sample directory |
|---|---|---|
| Original versus grayscale | original, grayscale | early.png |
| Original versus contrast enhancement | original, equalized, clahe | early.png |
| Gaussian versus median | grayscale, gaussian, median | early.png |
| Global versus Otsu versus adaptive | grayscale, global, otsu, adaptive | thresholds.png |
| Erosion versus dilation | otsu, erosion, dilation | morphology.png |
| Opening versus closing | otsu, opening, closing | morphology.png |
| Original versus selected processed OCR | original, pipeline_default | ocr_comparison.png |

All competing methods start independently from grayscale, except the four
morphologies, which independently start from grayscale Otsu. Gaussian/median
kernels are 3×3; Gaussian sigma is OpenCV's automatic 0 with reflected border,
median uses replicated border. Equalization uses 256 bins; CLAHE clip 2.0 and
8×8 tiles. Global cutoff 127; adaptive Gaussian block 31, C=11; Otsu's actual
cutoff is in each row. Morphology uses a 2×2 rectangle, anchor (1,1), one
iteration, neutral constant border, inverted white text foreground and restored
dark text output. Even kernels can introduce a directional shift.

The fixed production default remains **median3 → CLAHE2.0/8×8 → Otsu → no
morphology**, processed OCR. Full resolved per-sample settings are in JSON/CSV.
No per-image reference-based tuning or automatic ground-truth selection occurs.

## Final measured method table

CER = minimum unit-cost insertions + deletions + substitutions, divided by
normalized reference characters. Comparison copies use Unicode casefold,
whitespace collapse and trim; punctuation/numbers remain. Raw OCR and raw
references are retained separately. Empty references are rejected. A successful
blank OCR result scores 1; engine errors have null metrics and cause a failing
CLI exit after diagnostics are saved. **All 112 method calls and all 16 app calls
completed without engine/setup errors.**

| Method | Edits / reference chars | Pooled CER | Mean sample CER | Correct types | Present fields exact | Absent slots correct | No text |
|---|---:|---:|---:|---:|---:|---:|---:|
| original | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |
| grayscale | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |
| gaussian | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |
| median | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |
| equalized | 2442 / 2190 | 1.115068493 | 1.035231283 | 7/8 | 23/28 | 4/4 | 0 |
| clahe | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |
| global | 290 / 2190 | 0.132420091 | 0.126024590 | 7/8 | 24/28 | 4/4 | 1 |
| otsu | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |
| adaptive | 333 / 2190 | 0.152054795 | 0.141101695 | 7/8 | 24/28 | 4/4 | 0 |
| erosion | 1 / 2190 | 0.000456621 | 0.000423729 | 8/8 | 27/28 | 4/4 | 0 |
| dilation | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |
| opening | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |
| closing | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |
| pipeline_default | 0 / 2190 | 0.000000000 | 0.000000000 | 8/8 | 28/28 | 4/4 | 0 |

Pooled CER divides total edits by total reference length; mean CER gives each
sample equal weight. Every method has 8 scored samples and **2190 reference
characters**. CER can exceed 1 when spurious insertions dominate; it is not a
bounded accuracy percentage. The noisy equalized sample alone has CER 8.257627119.
Field scoring uses exact case-sensitive strings, separately from normalized CER.
There are **28 present field values** and **4 absent certificate-number slots**
per method; absent slots never inflate the present-value score.

## Unchanged production upload flow: observed type and fields

| Sample | Expected → observed type | Present fields | Original CER | Default CER | Readable / usable |
|---|---|---:|---:|---:|---|
| income_certificate_clear | income_certificate → income_certificate | 4/4 | 0 | 0.0 | True / True |
| income_certificate_low_contrast | income_certificate → income_certificate | 4/4 | 0 | 0.0 | True / True |
| caste_certificate_clear | caste_certificate → caste_certificate | 4/4 | 0 | 0.0 | True / True |
| caste_certificate_noisy | caste_certificate → caste_certificate | 4/4 | 0 | 0.0 | True / True |
| marksheet_clear | marksheet → marksheet | 3/3 | 0 | 0.0 | True / True |
| marksheet_slightly_blurred | marksheet → marksheet | 3/3 | 0 | 0.0 | True / True |
| identity_proof_clear | identity_proof → identity_proof | 3/3 | 0 | 0.0 | True / True |
| identity_proof_slightly_blurred | identity_proof → identity_proof | 3/3 | 0 | 0.0 | True / True |

The default upload flow returns exact expected fields (28/28 present values,
4/4 absent slots) and types (8/8), with all six stages and both OCR sources.
`integrated_observations.json` stores expected/observed values, raw results and
stage array hashes. The saved app report has **8 submitted files, 4 unique
required types detected, 4 unique types usable, 100% coverage/readiness, Ready**.
The four-clear-only and four-degraded-only submissions also each have 4/4 unique
detected/usable types and 100%; no additional OCR is implied by those report
recalculations. Duplicate related images do not add readiness credit.

## Adverse observations and rule diagnostics

| Sample / method | Edits / reference chars | CER | Observed outcome |
|---|---:|---:|---|
| income_certificate_low_contrast / global | 288 / 288 | 1.000000000 | doc_type: income_certificate → unknown; student_name: Asha Verma → None; certificate_number: INC-2026-0042 → None; application_id: APP-2026-0101 → None; issue_date: 2026-01-15 → None |
| caste_certificate_noisy / equalized | 2436 / 295 | 8.257627119 | doc_type: caste_certificate → unknown; student_name: Neel Rao → None; certificate_number: CST-2026-0043 → None; application_id: APP-2026-0102 → None; issue_date: 2026-01-16 → None |
| caste_certificate_noisy / adaptive | 333 / 295 | 1.128813559 | doc_type: caste_certificate → unknown; student_name: Neel Rao → None; certificate_number: CST-2026-0043 → None; application_id: APP-2026-0102 → None; issue_date: 2026-01-16 → None |
| caste_certificate_noisy / erosion | 1 / 295 | 0.003389831 | application_id: APP-2026-0102 → None |
| marksheet_slightly_blurred / equalized | 1 / 268 | 0.003731343 | OCR text differs outside supported fields; type and fields still match |
| identity_proof_slightly_blurred / equalized | 5 / 244 | 0.020491803 | issue_date: 2026-01-18 → None |
| identity_proof_slightly_blurred / global | 2 / 244 | 0.008196721 | OCR text differs outside supported fields; type and fields still match |

- Seven of 112 sample/method rows have nonzero CER; five rows have a type/field
  mismatch. Three type mismatches all return unknown (faint/global,
  noisy/equalized, noisy/adaptive). Zero engine failures. One no-text row.
- Global 127 makes every faint-income pixel white (0 dark pixels, stddev 0).
  Tesseract correctly reports no_text, classified unknown. This is a destructive
  demonstration alternative, not an engine/setup failure.
- Equalization expands background noise on the noisy caste page. Its 2436 edits
  include many spurious characters. Adaptive thresholding also preserves heavy
  speckle and breaks the title; a readable=True character-count heuristic can
  coexist with wrong text/unknown type. More contrast does not ensure usable OCR.
- Erosion weakens characters: `Application ID` becomes `Application 1D`, losing
  one optional field. On blurred identity/equalized, `Issue Date` becomes
  `tesue Date`, also missing an optional field. Both remain usable under the
  configured baseline because those fields are optional. Readiness does not
  certify correctness of every extracted value.
- For every sample, classify/extract on the reference transcript reproduces
  expected values. These are **reference-only diagnostic checks**, not extra OCR
  successes. Extracting actual OCR with the expected type is saved separately to
  show classification propagation. Observed method mismatches occur on damaged
  text; no peer-owned implementation defect was established. No guessed repair
  or keyword/regex change was made. Diagnostic attribution is not a causal proof.
- Original/default both have zero normalized CER. **No measured improvement**
  supports changing the fixed default. Other methods can damage already readable
  pages. Keep manual original selection; leave morphology optional.

## Artifacts and reproducibility

All paths below are relative to this checkout.

- `scripts/evaluate_dataset.py`: complete final runner; rejects nonempty output
  directories to avoid stale evidence/overwriting files. Works from another cwd.
- `outputs/experiments/SG05/metrics.json` and `.csv`: 112 sample/method rows,
  exact settings/contrast/histograms, raw and normalized text, CER, expected/
  observed types/fields, per-file usability, diagnostics and source hashes.
- `summary.csv`: 14 method totals; `original_processed.csv`: 8 paired default/
  original CER/contrast/settings rows.
- Each sample directory: 14 raw OCR texts, raw/normalized reference copies,
  13 processed alternatives, five figures (early, histogram, threshold,
  morphology, original/default). Original images remain in `dataset/`.
- `integrated_report.json` / `.md`, `integrated_observations.json`,
  `readiness_by_method.json`, `readiness_submissions.json`: real app results,
  alternative per-file checks and duplicate-safe checklist calculations.
- `artifact_sha256.json`: complete relative-file hash inventory (excludes itself).
  Deterministic report provenance retains the frozen M01 baseline after local
  evidence commits; source hashes identify the exact evaluated code.
- `outputs/experiments/SG05_environment.json`, `SG05_run.txt`, `SG05_tests.txt`,
  `SG05_reproducibility.json`: environment, real execution, full suite and repeat.

Commands (run in this checkout, independent repeat uses a fresh empty directory):

```bash
MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json outputs/experiments/SG05_environment.json
.venv/bin/python -m pip check
MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/evaluate_dataset.py
MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python -m unittest discover -s tests -v
MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/evaluate_dataset.py --output-dir /tmp/dip042-sg05-reproduce-20261110
.venv/bin/python -m compileall -q scripts/evaluate_dataset.py tests/test_metrics.py
git diff --check
```

Verification results: environment and `pip check` PASS; final full suite **107
PASS** (10.549s, exit 0), including six new SG05 accounting/artifact/integration
checks plus all prior regressions. Existing AppTest cases emit bare-mode
`ScriptRunContext` warnings; these are harness warnings, not OCR failures.
Syntax and `git diff --check` PASS. Full real rerun PASS (exit 0), and comparison
of complete file sets and SHA256 hashes gives **282/282 byte-identical files**.
The 282-file directory contains 112 raw OCR texts, 16 raw/normalized reference
copies, 104 alternative PNGs, 40 figure PNGs and 10 report/table/index files.
The repeat independently executes all 128 real OCR calls; the audit checks
stored evidence without replacing it. The reproducibility JSON stores both full
hash maps. No source changed after the final full suite/repeat.

## Visual review and limitations

Assistant opened the existing full contact sheet and these final generated
figures (no claim to have viewed every figure):

- `income_certificate_low_contrast/thresholds.png` and `ocr_comparison.png`;
- `caste_certificate_noisy/early.png`, `morphology.png`, `thresholds.png`;
- `income_certificate_clear/early.png`;
- `identity_proof_slightly_blurred/early.png`;
- `income_certificate_low_contrast/histograms.png`.

The inspected figures show white-out/global, noise amplification/equalization,
thin erosion strokes and the readable default. All figure/image files are also
decoded and verified by the audit; file decoding is not a human visual review.
Eight final figures were viewed; the list above is complete. No figure layout
problem was found in these inspected files.

Eight related, large-font generated pages sharing layout/vocabulary are an easy,
small evaluation set. No independent holdout, real scans, handwriting, uneven
lighting, rotations, multilingual text or severe degradation was evaluated.
OCR zero CER here ignores case/spacing and does not prove word layout or
extraction correctness. A focused test demonstrates that losing a line break
can preserve normalized CER=0 yet break field extraction. No generalization,
statistical confidence interval, fabricated human review or optimality claim.
Fictional document names differ across types; this checklist does not match
applicant identity across files. It checks configured presence/usable information,
not authenticity, cross-document consistency or official eligibility.

SG04 is retained as preliminary historical evidence. SG05 supersedes its role
for final measured tables, pending M02 freeze. No earlier result is invalidated:
production settings, sources and modules are unchanged. M02 must combine this
with JB05 browser evidence and check source fingerprints before freezing.
SG06/report writing is gated by M02. No outstanding peer/dependency request.
