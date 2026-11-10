# Sakshi Gupta — Personal sprint handoff

> A new chat receiving this file's path must execute **Sakshi's next eligible SG sprint only**, update this handoff in her own checkout, and stop. Do not start Jigisha's work or a merge automatically.

## Current position

- Owner: **Sakshi Gupta**.
- Role: image dataset, DIP pipeline, OCR, experiments, academic report; integration lead in separate M chats.
- Updated: 2026-11-10 15:11 Asia/Kolkata; **SG05 DONE**, verified locally and READY FOR M02; not merged.
- Active sprint: none; **SG05 completed and verified**.
- Next: **M02 in a separate merge chat**, after both SG05/JB05 are verified. **SG06 remains gated by M02** and its frozen evidence.
- Checkout: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi`. Branch: `codex/sakshi-dip`.
- GitHub repository: `https://github.com/guptasakshi06/Graphia`; shared remote `origin`; matching remote branch `origin/codex/sakshi-dip`. Initial M00 history published by user request; further pushes require user instructions.
- M00 baseline: single root commit named `M00` (resolve with `git rev-list --max-parents=0 HEAD`). The user requested one commit instead of three intermediate setup commits. Verified local `.venv`: Python 3.12.3; all six imports, `pip check`, Streamlit CLI and Tesseract 5.3.4 (`eng`, `osd`) PASS. Evidence: `docs/merge/M00-environment-sakshi.json` and `docs/merge/M00-environment-comparison.json`. Code/dependencies are unchanged by the history cleanup.
- Build readiness: **SG01–SG04 DONE and integrated at M01**; both source cutoffs verified by the merge chat.
- Code/evidence merged: SG01–SG04 at M01; **SG05 final local measurements DONE, not merged/frozen**. Validation: `docs/validation/sakshi.md`; artifacts: `outputs/experiments/SG05/`.
- Peer requests: none.

Before M00 use the root `MERGE_HANDOFF.md` for shared setup. After M00 use **this file in Sakshi's checkout**, not a stale root copy. Read `HANDOFF.md`, `PROJECT_BRIEF.md`, `TEAM_CONTRACT.md` and `AGENTS.md` first. Contract APIs are fixed across tracks. Keep your own handoff current; do not change the master, Jigisha's handoff, or shared dependencies during parallel work.

## Sprint ledger

| Sprint | Day | Target | Depends on | Status | Integrated at |
|---|---|---:|---|---|---|
| SG01 | 1 | 60 min | M00 | DONE | M01 (DONE, synchronized) |
| SG02 | 1 | 75 min | SG01 | DONE | M01 (DONE, synchronized) |
| SG03 | 1 | 75 min | SG02 | DONE | M01 (DONE, synchronized) |
| SG04 | 1 | 75 min | SG03 | DONE | M01 (DONE, synchronized) |
| SG05 | 2 | 75 min | SG04, M01 | DONE | Not merged; READY FOR M02 |
| SG06 | 2 | 90 min | SG05, M02 | TODO | Not merged; target M03 |

## SG01 — Dataset and correct image input

**Build:** A reproducible sample set and image loader. You do not depend on Jigisha's implementations; use the frozen field labels/type IDs in `TEAM_CONTRACT.md`.

1. Verify you are in Sakshi's checkout on the recorded branch; verify your local environment using the M00 setup instructions. Never assume the other checkout's `.venv` applies here.
2. Explain pixels, shape/dtype, BGR/RGB, resolution and resize interpolation. Explain why reference text must exist before OCR experiments.
3. Use student-supplied fictional/reusable images if available. Otherwise create `scripts/create_sample_dataset.py` with Pillow: four clear fictional document types plus four degraded derivatives, approximately eight images total. Add a visible synthetic/sample label without pretending these are official certificates. Cover low contrast, seeded noise and slight blur; record deterministic seeds/settings.
4. Follow the contract's sample title/field labels. Include names on all samples and labeled certificate numbers on the two certificate types; include issue date and application ID where reasonable. Do not force every field onto every type.
5. Create `dataset/manifest.json`, ground-truth text and expected fields. Record type, condition, provenance, derivative relationship, settings and reference path. Manually inspect rendered images against transcripts; label reference text unverified until actually checked.
6. Implement `load_image(source, max_dimension=1800)` in `modules/preprocessing.py` according to the contract: paths/bytes, orientation, alpha-to-white, BGR, aspect ratio and invalid-input handling.
7. Save and inspect a contact sheet. Check all manifest paths, decodes, dimensions and colors. Do not start filtering yet.

**Owned outputs:** `dataset/**`, `scripts/create_sample_dataset.py`, loading portion of `modules/preprocessing.py`, relevant `tests/test_preprocessing.py`, `outputs/experiments/contact_sheet.png`, `docs/sprint_notes/SG01.md`.

**Acceptance:** Approximately eight decodable samples; all four types/quality variations represented; ground truth visually verified; path and bytes loading both work; an invalid image fails clearly; colors/orientation/aspect ratio are correct.

**Handoff:** Record generation/verification commands, chosen resize policy, sample provenance and field coverage. Mark SG01 done only with evidence, then stop. Next SG02.

## SG02 — Grayscale, denoising, contrast and histograms

**Build:** Explainable DIP functions and a repeatable experiment runner.

1. Teach approximate grayscale weights, weighted Gaussian neighborhoods, median selection with a small numeric example, and the noise/detail tradeoff.
2. Extend preprocessing with grayscale, Gaussian and median filtering. Validate kernels and preserve the original image array.
3. Implement histogram equalization and CLAHE; explain histograms, local tiles and clipping. Record CLAHE settings rather than hiding defaults.
4. Create `scripts/run_experiments.py` to compare original/grayscale, Gaussian/median and original/equalized/CLAHE on the same inputs. Do not chain competing methods by default.
5. Save figures/histograms and actual grayscale standard-deviation contrast values. Explain that this simple contrast measure is not OCR accuracy and high contrast need not improve text.
6. Inspect a clean, a noisy and a low-contrast image. Record any smoothing/enhancement that damages text or amplifies noise.

**Owned outputs:** Preprocessing functions, experiment script, focused preprocessing checks, `outputs/experiments/**`, SG02 teaching notes.

**Acceptance:** Expected shapes/dtypes; unchanged input; valid/invalid kernel checks; actual comparison images and contrast values saved. Do not claim an OCR improvement yet.

**Handoff:** Record exact settings and provisional recommendations. Stop; next SG03.

## SG03 — Thresholds, morphology and contract pipeline

**Build:** All required threshold and morphology demonstrations and `run_pipeline`.

1. Explain a simple global cutoff, Otsu's variance intuition and adaptive thresholds under uneven lighting.
2. Implement global, Otsu and adaptive thresholding. Validate adaptive odd block size greater than one; report selected Otsu threshold.
3. Explain structuring elements and white foreground. Implement erosion, dilation, opening and closing. Invert deliberately for morphology if needed; restore dark-text/light-background before OCR.
4. Implement the exact `run_pipeline(image_bgr, options=None)` API and output keys from `TEAM_CONTRACT.md`. Every named stage remains available when bypassed. Reject invalid option names/values. Return resolved JSON-safe parameters.
5. Extend comparisons to global/Otsu/adaptive, erosion/dilation, opening/closing. Inspect where operations remove noise or damage character strokes.
6. Keep a small practical candidate set and optional morphology; do not run an exhaustive parameter search.

**Owned outputs:** Complete `modules/preprocessing.py`, runner updates, focused checks, comparison artifacts, SG03 notes.

**Acceptance:** Three threshold and four morphology methods all execute with visible output; polarity is verified; image arrays match the contract; original remains unchanged; required parameters/defaults are documented.

**Handoff:** Record exact public API availability and any requested contract changes for M01. Stop; next SG04.

## SG04 — Real OCR and preliminary CER

**Build:** Tesseract wrapper and honest original/processed comparison. This finishes Sakshi's pre-merge code.

1. Explain OCR as a downstream recognition stage, how Tesseract uses page segmentation, and why Python Pytesseract needs the system executable.
2. Implement `extract_text` in `modules/ocr.py` exactly as contracted. Detect missing engine/language data, enforce timeout and handle blank text. Confidence, if exposed, excludes invalid entries and is labeled heuristic.
3. Run OCR on original and selected processed images; store actual text, settings and errors. Do not let failure become a successful empty result.
4. Add a small CER utility to the experiment runner: Levenshtein distance / reference character count. Document normalization and empty-reference behavior; CER may exceed 1. Verify known insertion/deletion/substitution examples.
5. Run preliminary dataset comparisons using verified transcripts. Save raw texts and CSV/JSON metrics. Compare at least clear and degraded inputs; ideally run all eight within this sprint.
6. Select a documented default pipeline based on actual demo results. Keep original/grayscale alternatives when preprocessing hurts; do not use ground truth to automatically choose a production output per uploaded image.

**Owned outputs:** `modules/ocr.py`, `tests/test_ocr.py`, `tests/test_metrics.py`, experiment outputs, SG04 notes.

**Acceptance:** Clear image yields real OCR text; original/processed outputs and CER exist; no-text and setup/error states are tested; contract returns match; no fabricated improvement. A missing system engine means this sprint is not done.

**Handoff:** Mark build package READY FOR M01 with changed-file list, executed checks, branch tip/local diff, dataset paths and OCR artifact paths. Do not claim merged. Stop and provide the root `MERGE_HANDOFF.md` path. SG05 must wait for M01 and synchronize to the merged baseline.

## SG05 — Integrated pipeline evaluation and final experiments

**Build:** Final measured evidence from real merged modules, including Jigisha's classifier/extractor.

1. Verify `docs/merge/M01.md` and actual merged code exist. Synchronize your clean branch from integration following the merge handoff; record the baseline. Do not rely only on a stale master status.
2. Run all samples through actual image → DIP → OCR → classification/extraction → readiness code. Add `scripts/evaluate_dataset.py` if useful. Compare expected/observed types and supported fields; distinguish OCR failures from rule failures.
3. Re-run all seven DIP/OCR comparisons with final settings. Save final tables with sample IDs, exact methods/settings, contrast and original/processed CER, plus raw OCR/reference normalization.
4. Document incorrect classifications, missed fields, no-text/worse-preprocessing cases and dataset limitations. Use actual denominators for counts/accuracy; do not inflate certainty from eight related samples.
5. Fix only your owned bugs, then rerun affected checks. Send peer-owned bug requests through this handoff; M02 must resolve them before evidence freezes.
6. Write `docs/validation/sakshi.md` and distinguish final data from preliminary SG04 output. Mark invalidated artifacts if settings changed.

**Owned outputs:** Final `outputs/experiments/**`, evaluation script, Sakshi validation summary, relevant module fixes, SG05 notes.

**Acceptance:** All final tables can be reproduced; ground truth checked; all seven comparisons represented; observed type/field results recorded; limitations and failures are honest. No report prose or slides claiming unverified improvements.

**Handoff:** Mark READY FOR M02 with artifact paths and unresolved peer requests. Stop; SG06 requires M02's frozen evidence.

## SG06 — Academic report and DIP/OCR viva material

**Build:** A report based on the frozen integrated results. Jigisha separately handles slides/diagrams/app viva.

1. Verify M02 has frozen measurements and browser results. Use its exact output paths; do not substitute preliminary numbers.
2. Write `docs/project_report.md` with Abstract, Introduction, Problem Statement, Objectives, Existing Approach, Proposed Methodology, DIP Techniques, System Architecture, Implementation, Experimental Results, Limitations, Future Scope, Conclusion and References.
3. Use the known student names Sakshi Gupta and Jigisha Baiswar. Leave clearly labeled placeholders only for missing roll numbers, college, department, faculty and required cover format.
4. Include actual measured tables and DIP figures. Diagrams will be supplied by Jigisha in JB06; use agreed paths `docs/diagrams/architecture.png` and `docs/diagrams/workflow.png`. If they are not available yet, do not mark rendering complete: use a labeled placeholder and let M03 insert/re-render the final diagrams. Do not recreate competing diagrams in her directory.
5. Produce an editable college report and usable DOCX, with PDF if practical. Read and apply relevant document/PDF skills when generating artifacts, render and inspect pages. Keep layout simple; do not claim visual verification without doing it.
6. Write `docs/viva_sakshi.md` covering project choice/DIP relevance, grayscale, histograms/CLAHE, Gaussian versus median, global/Otsu/adaptive thresholding, erosion/dilation/opening/closing, OCR/Tesseract and experiments. Give natural beginner-level answers and small mathematical examples.
7. Record source URLs actually consulted; never invent citations, experiments or features. Label future improvements honestly.

**Owned outputs:** Report Markdown/DOCX/optional PDF, `docs/report_assets/**`, `docs/viva_sakshi.md`, SG06 notes.

**Acceptance:** Required report sections exist; figures/results match M02; names correct; report opens/renders; no false capability claims; viva explanations are technically sound. Record final diagram insertion as an explicit M03 assembly task if needed.

**Handoff:** Mark READY FOR M03 and list all artifacts, rendering evidence, any remaining assembly/metadata items. Stop. Do not claim final project merge or submission.

## Update this handoff after every session

Update the current position, own ledger, active/next sprint, branch/checkout, merge-readiness and peer requests. Do not edit the shared master during parallel work. Append a record using this template; preserve previous records:

```markdown
### SGxx — YYYY-MM-DD HH:MM Asia/Kolkata — session N
- Status before → after:
- Checkout / branch / baseline / commit or dirty diff:
- Checkpoints completed and concepts explained:
- Changed owned files:
- Checks: exact command, actual result, PASS/FAIL/NOT RUN:
- Evidence paths and teaching notes:
- Acceptance still unmet / errors / student-only action:
- Requested peer or dependency changes:
- Remaining work and exact resume action:
- Next eligible sprint or merge gate:
- Merge readiness: NOT READY / READY; merged at: not yet / gate + commit:
```

## Session history

2026-11-10: Personal track planned. All SG sprints TODO; no code, dataset, environment checks or merges performed.

### M00 foundation annotation — 2026-11-10 12:43 Asia/Kolkata
- This integration-session setup annotation does not execute a personal sprint. All personal sprint statuses remain TODO; no code/evidence has been merged at M01.
- Actual checkout/branch: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi` / `codex/sakshi-dip`. Created from common setup baseline `09893da4d1fea88d985baa12c0c77221c9750a4e`.
- In this checkout: `python3 -m venv .venv` and `.venv/bin/python -m pip install --no-cache-dir --no-index --find-links /tmp/dip042-wheelhouse -r requirements.txt -c docs/merge/M00-requirements-lock.txt`: PASS. The /tmp wheel cache is local convenience only; future machines install from the package index.
- In this checkout: `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/docs/merge/M00-environment-sakshi.json`: PASS; `.venv/bin/python -m pip check`: PASS; `.venv/bin/python -m streamlit --version`: PASS (1.67.0).
- Independent venv prefix verified; `.venv/bin/python -m pip freeze` matches all 42 distributions in the common M00 snapshot. System Tesseract is shared on this machine; Python environments are separate.
- Contract v1 frozen without signature/schema changes. No human walkthrough, dataset evaluation or application success claimed.
- Shared foundation record will be synchronized from integration before this sprint begins. Use only your own handoff after that sync; master/peer handoffs are snapshots.
- Next action after M00 DONE: read this handoff in this checkout and execute **SG01 only**. Do not implement the peer track or the next merge gate.

### M00 completed — 2026-11-10 12:46 Asia/Kolkata
- M00 DONE. Shared setup baseline `09893da4d1fea88d985baa12c0c77221c9750a4e`; verified foundation record `01b3e869f64a7c58f2c4aee31e0cd65cf25c1058` was forward-merged into this clean personal checkout using `git merge --ff-only codex/integration`.
- Own handoff, contract, requirements, environment checker and shared records were compared with integration after the sync: PASS. All environment checks above passed on this machine. Final completion metadata is documentation only and is synchronized before this chat ends.
- No personal sprint executed; all sprint ledger rows remain TODO; no personal code/evidence merged at M01. No open peer/dependency requests.
- Exact next action: in a new personal chat, request execution of **SG01 only** using `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md`. Work in this checkout and update this copy of the handoff. Do not edit the root/peer handoffs or shared requirements during personal work.

### GitHub setup annotation — 2026-11-10 12:53 Asia/Kolkata
- User requested initial publication to `https://github.com/guptasakshi06/Graphia`. Initial M00 tip `7cc5a4f` was pushed to `main` and all three codex branches; this checkout stays on `codex/sakshi-dip`.
- Remote guidance is included in the single M00 commit and synchronized before this chat ends. No personal sprint, dataset, application or test result changed. All sprint statuses remain TODO; work in this checkout using this handoff.

### One-commit baseline correction — 2026-11-10 12:56 Asia/Kolkata
- User requested replacing the three intermediate setup commits with one root commit named `M00`. Keep this checkout on its existing codex branch and start from that root baseline. Historical hashes above describe pre-squash activity only; current baseline is obtained with `git rev-list --max-parents=0 HEAD`. Setup/evidence files and TODO sprint statuses are preserved.

### SG01 start — 2026-11-10 13:03 Asia/Kolkata — session 1
- Status: TODO → IN_PROGRESS. Read own/shared agreements and M00 evidence.
- Checkout: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi`; branch `codex/sakshi-dip`; actual HEAD/root baseline `464c884af09bb1d2db686559eaee16cdb9912d59` (`M00`); clean at start.
- No supplied dataset found. Plan: deterministic Pillow fictional samples, reference text/fields, loader, contact sheet, focused tests and visual inspection. References remain unverified until inspected.
- Scope: SG01 only; no filtering, OCR, peer/shared edits or publication.

### SG01 checkpoint — 2026-11-10 13:07 Asia/Kolkata — session 1
- Own environment rechecked: six imports, independent venv, Tesseract 5.3.4 (`eng`, `osd`), `pip check` and Streamlit CLI PASS. Evidence: `outputs/experiments/SG01_environment.json`.
- Eight fictional PNGs generated with reference text and expected fields; four types, low contrast, seeded noise and mild blur represented. Six image-loader tests PASS.
- Contact sheet and four full-size degraded pages inspected against all eight transcripts. No clipping or mismatches found; hash-bound inspection recorded in `dataset/visual_review.json`. This was assistant inspection, not human review.
- Remaining before DONE: full dataset/integrity/reproducibility tests, syntax/diff check, teaching notes and final handoff. No blocker or peer request.

### SG01 completion — 2026-11-10 13:08 Asia/Kolkata — session 1
- Status before → after: TODO → IN_PROGRESS → **DONE**. All SG01 acceptance checks met; SG02–SG06 remain TODO.
- Checkout / branch / baseline: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi` / `codex/sakshi-dip` / `464c884af09bb1d2db686559eaee16cdb9912d59` (`M00`). HEAD remains M00. Changes are local, uncommitted and unmerged; no push performed. Clean at start; only owned paths changed.
- Concepts explained before implementation and in `docs/sprint_notes/SG01.md`: pixels, `(height, width, channels)`, uint8, BGR/RGB, resolution, EXIF orientation, alpha-on-white, aspect ratio, area interpolation, and why verified references precede OCR.
- Dataset checkpoint: eight fictional RGB PNGs, each 1400 × 1000, four types with four clear parents/four derivatives. Income low contrast (`scale=0.22`, `offset=185`); caste Gaussian noise (`seed=4201`, `sigma=18`); marksheet/identity mild Gaussian blur (`radius=1.2`/`1.5`). Seeds/settings, font/version hashes, provenance, parent IDs, full reference paths and expected fields are in `dataset/manifest.json`. No private data or official form claims.
- Field coverage: name, application ID and ISO issue date on every sample; labeled certificate numbers on income/caste certificates only. Marksheet/identity certificate numbers are `null`. Eight full transcripts include banners and disclaimers; these are reference/test text, not OCR output.
- Visual checkpoint: inspected all eight pages in `outputs/experiments/contact_sheet.png` against transcripts and all four degraded PNGs individually. All text/fields matched, no clipping; intended conditions visible. `dataset/visual_review.json` records assistant inspection and image/reference hashes; no human review claimed. Regeneration cannot create a new review; changed hashes require reinspection.
- Loader checkpoint: `load_image(source, max_dimension=1800)` accepts path/bytes; EXIF applied, transparency composited on white, output BGR uint8, no enlargement, aspect-preserving downsampling with `INTER_AREA` and nearest whole-pixel dimensions. Source limit 40,000,000 pixels before decoding plus Pillow bomb guard. All samples stay 1400 × 1000 at default; tested 2400 × 1200 → 1800 × 900, portrait → 900 × 1800, sample limit 700 → 700 × 500. Invalid inputs/limits fail with `ValueError`. Contract unchanged; no filtering/pipeline/OCR implemented.
- Changed owned files: `SAKSHI_HANDOFF.md`; `modules/preprocessing.py`; `scripts/create_sample_dataset.py`; `tests/test_preprocessing.py`; `dataset/README.md`, `dataset/manifest.json`, `dataset/visual_review.json`, eight PNGs in four type directories, eight `dataset/references/*.txt`; `outputs/experiments/contact_sheet.png`, `outputs/experiments/SG01_environment.json`, `outputs/experiments/SG01_tests.txt`; `docs/sprint_notes/SG01.md`.
- Checks / actual results:
  - `git status --short --branch`, `git worktree list --porcelain`, `git log -1 --format='%H %s'`: PASS; correct owner checkout/branch and actual M00 baseline.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json outputs/experiments/SG01_environment.json`: PASS; Python 3.12.3, own venv, all six imports; Tesseract 5.3.4 with `eng`/`osd`.
  - `.venv/bin/python -m pip check`: PASS, no broken requirements (cache permission warning only). `.venv/bin/python -m streamlit --version`: PASS, 1.67.0.
  - `.venv/bin/python scripts/create_sample_dataset.py`: PASS, eight samples plus manifest/transcripts/contact sheet.
  - `.venv/bin/python -m unittest discover -s tests -p test_preprocessing.py -k ImageInput -v`: PASS, six loader tests.
  - `.venv/bin/python -m unittest discover -s tests -p test_preprocessing.py -v > outputs/experiments/SG01_tests.txt 2>&1`: PASS, **8 tests**, including path/bytes, BGR, EXIF pixel placement, alpha/palette, grayscale input, resize/no enlargement, invalid/corrupt/truncated input, source-pixel guard, all dataset paths/decodes/dimensions/fields/review hashes, and byte-identical fresh generation in a temporary directory.
  - `.venv/bin/python -m compileall -q modules/preprocessing.py scripts/create_sample_dataset.py tests/test_preprocessing.py`: PASS. `git diff --check`: PASS.
- Acceptance unmet / errors / student-only action: none. No OCR accuracy, filtering improvement, application success or student review claimed.
- Requested peer/dependency changes: none. Shared/peer files and dependencies untouched.
- Remaining work: SG02–SG04 before Sakshi's package is ready for M01; later validation/report remain gated. Stop after SG01.
- Exact next action: in a new chat request `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md and execute SG02. Verify the work and update the handoff before stopping.`
- Merge readiness: **SG01 complete locally; NOT READY for M01** until SG04 and peer build prerequisites pass. Merged at: **not yet**.

### SG01 Git publication request — 2026-11-10 13:12 Asia/Kolkata
- User explicitly requested committing this sprint to GitHub with a one-line explanation.
- Commit subject: `SG01: Add reproducible sample documents and a tested image loader`. Destination: `origin` → `https://github.com/guptasakshi06/Graphia.git`, branch `codex/sakshi-dip`. Only Sakshi-owned SG01 work is included.
- Before publication, `git ls-remote origin refs/heads/codex/sakshi-dip` confirmed remote base `464c884af09bb1d2db686559eaee16cdb9912d59` matches local M00. The sandbox's first attempt could not resolve GitHub; authorized network access succeeded.
- Resolve the sprint commit with `git log -1 --format='%H %s'`; publication is checked by comparing `git rev-parse HEAD` with `git ls-remote origin refs/heads/codex/sakshi-dip`. The actual push result is reported in this chat.
- SG01 remains DONE; not integrated at M01. Next: SG02 in this checkout. No merge, peer work, dependency change or later sprint is included.

### SG02 start — 2026-11-10 13:14 Asia/Kolkata — session 1
- Status: TODO → IN_PROGRESS. Read AGENTS/master/brief/contract/own handoff and M00 foundation evidence. SG01 prerequisite exists in actual commit `6629e0f240023aadb8027032f1e60b6071e34d27`; M00 root `464c884af09bb1d2db686559eaee16cdb9912d59`.
- Checkout/branch: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi` / `codex/sakshi-dip`; clean at start. No branch switch, merge or peer/shared edit needed.
- Explained grayscale weights, Gaussian weighted neighborhoods, median example, detail tradeoff, histograms and global/local clipped enhancement before coding.
- Plan: independent grayscale/filter/contrast helpers, repeatable SG02 experiment runner, focused checks and visual inspection of clear/noisy/low-contrast samples. SG03 pipeline/threshold/morphology and OCR stay pending.
- No blockers or dependency/peer requests. Update here at checkpoints and completion; no publication requested.

### SG02 checkpoint — 2026-11-10 13:18 Asia/Kolkata — session 1
- Implemented independent `to_grayscale`, `denoise_image` and `enhance_contrast` helpers. Input/type/kernel/CLAHE validation and copy behavior tested; original loader preserved.
- `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json outputs/experiments/SG02_environment.json`: PASS; own venv and all six imports available. Initial preprocessing suite: 14 tests PASS (Matplotlib default-cache warning only; subsequent commands use writable MPLCONFIGDIR).
- Runner executed for all eight samples: 48 measured rows, independent alternatives, 48 full-size PNGs, eight comparison figures, eight detail figures and eight histogram figures. Adjusted detail crop/layout after inspection to avoid slicing the title; regenerated outputs.
- Inspected full-page clear income, low-contrast income and noisy caste comparisons, their corrected detail crops, and low-contrast/noisy histogram figures. Equalization strongly expands low contrast but amplifies noisy background; CLAHE is milder at clip 2/grid 8x8. Gaussian softens edges; median rounds some corners. No lost field line observed at these settings; no OCR inference made.
- Next before DONE: saved-output audit, reproducibility comparison, final tests/notes/handoff. No blocker, contract change or peer request.

### SG02 completion — 2026-11-10 13:21 Asia/Kolkata — session 1
- Status before → after: TODO → IN_PROGRESS → **DONE**. SG02 acceptance met; SG03–SG06 remain TODO. Stop after this sprint.
- Checkout / branch / baseline / local diff: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi` / `codex/sakshi-dip`; HEAD `6629e0f240023aadb8027032f1e60b6071e34d27` (SG01), M00 root `464c884af09bb1d2db686559eaee16cdb9912d59`. Clean at start; SG02 changes are local/uncommitted/unmerged. No commit/push requested in this chat; none performed.
- Concepts explained before coding and in `docs/sprint_notes/SG02.md`: grayscale BGR weights; 3x3 Gaussian weighted neighborhood; numeric median example; noise/detail tradeoff; 256-bin histograms; global equalization; local clipped CLAHE; grayscale population standard deviation versus OCR accuracy.
- Functions available: existing `load_image` preserved; added `to_grayscale(image_bgr)`, `denoise_image(gray, method="median", kernel_size=3)`, `enhance_contrast(gray, method="clahe", clip_limit=2.0, tile_grid_size=(8,8))`. Helpers validate nonempty uint8 arrays and appropriate channel shapes; filters validate positive odd kernels; contrast validates methods, finite positive clip limit and positive integer tile grid. Results/copies do not share input memory. Contract public defaults unchanged; `run_pipeline` remains SG03 work.
- Exact experiment settings: no resize of these 1400x1000 samples under 1800 limit; Gaussian/median **3x3**; Gaussian `sigmaX=0`, `BORDER_REFLECT_101`; median replicated borders. Global histogram equalization; CLAHE **clipLimit=2.0, tileGridSize=(8,8)**. Each alternative starts from original/grayscale, not the preceding competing method. Display fixed gray range 0–255, BGR→RGB only for plotting, shared detail crop `(65,190,1100,420)`.
- Runner: all eight hash-verified fictional samples, six alternatives each, **48 measured rows**, 48 full-size method PNGs plus 24 comparison/detail/histogram figures. CSV/JSON include exact settings, versions, source hashes and grayscale contrast; JSON includes shapes/dtypes and all 256 histogram counts. Original contrast uses grayscale conversion, so it equals grayscale contrast.
- Visual evidence: assistant inspected full-page clear income, low-contrast income and noisy caste comparisons; corrected crops for all three; low-contrast/noisy histograms. All 24 figure files decode, but no visual inspection of the other five comparison sets or student review is claimed. Gaussian softens character edges; median rounds some corners; no field line vanished in inspected outputs. Equalization makes low-contrast text darker but amplifies noisy background strongly. CLAHE is milder at these settings and still amplifies noisy speckle.
- Actual examples (grayscale stddev, not accuracy): clear income original **42.3519**, Gaussian **38.1779**, median **42.0576**; low-contrast income original **9.3507**, equalized **55.7899**, CLAHE **10.8864**; noisy caste original **42.4010**, equalized **97.9022**, CLAHE **47.9676**. Full eight-sample table is in SG02 notes/metrics.
- Provisional recommendations: keep original/grayscale for clean documents; compare equalization for uniformly faint pages; compare denoising before enhancement on noisy pages. Keep the small alternative set; do not infer OCR improvement or change contract defaults until real OCR comparisons. No OCR, thresholds, morphology or end-to-end application success claimed.
- Changed owned files: `modules/preprocessing.py`, `scripts/run_experiments.py`, `tests/test_preprocessing.py`, `docs/sprint_notes/SG02.md`, `SAKSHI_HANDOFF.md`; generated `outputs/experiments/SG02/**` (74 files), `outputs/experiments/SG02_environment.json`, `outputs/experiments/SG02_tests.txt`, `outputs/experiments/SG02_reproducibility.json`. Dataset and SG01 outputs unchanged; peer/shared files untouched.
- Checks / exact commands and real results:
  - `git status --short --branch`, `git worktree list --porcelain`, `git log -2 --format='%H %s'`: PASS; correct personal branch/worktree; actual SG01 prerequisite commit and M00 root verified.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json outputs/experiments/SG02_environment.json`: PASS, own Python 3.12.3 venv, all six imports and Tesseract setup available. This is environment evidence only.
  - `.venv/bin/python -m unittest discover -s tests -p test_preprocessing.py -v`: initial **14 tests PASS**; Matplotlib default-cache warning only. Subsequent commands set a writable MPLCONFIGDIR.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/run_experiments.py`: PASS, **48 rows / 8 samples**; rerun after crop/layout correction also PASS.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python -m unittest discover -s tests -p test_preprocessing.py -v > outputs/experiments/SG02_tests.txt 2>&1`: PASS, **15 tests**, including previous SG01 checks, known numerical DIP cases, input preservation, invalid settings, independent comparisons and saved-output audit. Audit recomputes all saved metrics/histograms, checks source hashes and original pixels, and verifies all 24 figure PNGs.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/run_experiments.py --output-dir /tmp/dip042-sg02-reproduce`: PASS. Python file-set/byte comparison with saved SG02 output: **74/74 files identical**, including figures and CSV/JSON. Command and artifact SHA256 values recorded in `outputs/experiments/SG02_reproducibility.json`.
  - `.venv/bin/python -m compileall -q modules/preprocessing.py scripts/run_experiments.py tests/test_preprocessing.py`: PASS. `git diff --check`: PASS.
- Acceptance still unmet / errors / student-only action: none for SG02. No fabricated data, OCR claim or human review. No external source citations used; observations come from executed local experiments.
- Requested peer or dependency changes: none. `HANDOFF.md`, `MERGE_HANDOFF.md`, `TEAM_CONTRACT.md`, `requirements.txt` and peer paths unchanged.
- Remaining: SG03 thresholds/morphology/exact contract pipeline, then SG04 real OCR/CER before M01. No later sprint started.
- Exact next action in a new chat: `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md and execute SG03. Verify the work and update the handoff before stopping.`
- Merge readiness: **SG02 complete locally; NOT READY for M01** until SG04 and peer build prerequisites pass. Merged at: **not yet**.

### SG02 local commit request — 2026-11-10 13:22 Asia/Kolkata
- User requested committing the completed sprint locally. Include all SG02 owned code, tests, notes and experiment evidence, plus this handoff update, in one commit on `codex/sakshi-dip`.
- Commit subject: `SG02: Add tested grayscale, denoising and contrast experiments`.
- Resolve the resulting commit with `git log -1 --format='%H %s'`; verify the checkout with `git status --short --branch`. The earlier uncommitted statements describe the pre-commit sprint checkpoint.
- Pre-commit `git diff --check`: PASS; all pending paths belong to Sakshi's SG02 work. Existing verification remains 15 tests PASS and 74/74 experiment files reproduced identically; no code changes since those checks.
- This is a local commit only; no push or merge. SG02 remains DONE; next SG03 in this checkout. M01 readiness remains NOT READY pending SG04 and peer prerequisites.
- Staged verification: ordinary `git diff --cached --check` flags CSV writer CRLF line endings as trailing whitespace. `git -c core.whitespace=cr-at-eol diff --cached --check`: PASS, recognizing those CSV line endings; experiment files and their verified hashes are preserved. Reviewed staged paths: all 82 files are Sakshi-owned SG02 code, evidence and notes.

### SG03 start — 2026-11-10 13:28 Asia/Kolkata — session 1
- TODO → IN_PROGRESS. Read project AGENTS/master/brief/contract, this live handoff and M00 evidence. Root Git policy supplied by user takes precedence over stale publication guidance in this checkout.
- Checkout: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi`; branch `codex/sakshi-dip`; clean at start. Actual SG02 prerequisite commit `f4e0a363e0bfc610d3ba73b754bfaef924c8c703`; SG01 `6629e0f`; M00 root `464c884`. No merge performed.
- Explained threshold cutoff example, Otsu grouping, local adaptive thresholds, white foreground and deliberate morphology inversion before coding.
- Plan: validated threshold/morphology helpers, exact contract-v1 pipeline, independent comparison artifacts, numerical and contract checks, visual inspection, notes and local commit with Sakshi's worktree-specific identity. No OCR or later sprint work.
- No blocker or peer/dependency request. Existing `extensions.worktreeConfig=true`; owner identity will be set only for this worktree before committing.

### SG03 checkpoint — 2026-11-10 13:32 Asia/Kolkata — session 1
- Implemented `threshold_image`, `apply_morphology` and exact `run_pipeline(image_bgr, options=None)` contract-v1 API. All nine public defaults preserved; bypass stages and OCR input are independent copies; Otsu cutoff and fixed settings are JSON-safe parameters. No shared/peer changes.
- Environment PASS in own venv. Existing 15 regression checks PASS after implementation. First new focused run: 9 functional checks PASS, artifact audit ERROR because metrics were still being generated; runner then completed. Sequenced full rerun after generation: **25 tests PASS**, including artifact audit. No unresolved test failure.
- Generated 72 measured alternatives, 48 default stage PNGs and 32 comparison figures for 8 samples (154 SG03 files with CSV/JSON). Thresholds start from common grayscale; four morphology alternatives start independently from its Otsu result. Default pipeline saved separately.
- Assistant visually inspected clear-income full thresholds, low-contrast-income full thresholds and detail, noisy-caste thresholds/detail morphology, clear-income morphology detail and blurred-marksheet threshold/morphology details. Global 127 erases faint sample; Otsu 218 restores visible text; adaptive adds noisy background; erosion damages thin strokes; dilation thickens strokes. Opening/closing change geometry subtly. Polarity verified by numerical tests. No human review or OCR claim.
- Remaining: reproducibility and SG02 compatibility reruns, notes/final handoff, syntax/diff checks and owner-authored local commit. No blocker or peer request.

### SG03 completion — 2026-11-10 13:35 Asia/Kolkata — session 1
- Status: TODO → IN_PROGRESS → **DONE**. All SG03 acceptance checks met. SG04–SG06 remain TODO; no later sprint or merge performed.
- Checkout/branch: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi` / `codex/sakshi-dip`. Start HEAD/prerequisite SG02 `f4e0a363e0bfc610d3ba73b754bfaef924c8c703`; SG01 `6629e0f240023aadb8027032f1e60b6071e34d27`; root M00 `464c884af09bb1d2db686559eaee16cdb9912d59`. Clean at start; all sprint changes belong to Sakshi.
- Implemented global/Otsu/adaptive thresholding, four morphology methods and complete contract-v1 `run_pipeline(image_bgr, options=None)`. Existing loader/grayscale/filter/contrast behavior preserved. API returns exactly `stages`, `ocr_input`, `parameters`; original BGR and five 2D gray/binary stages remain present. All arrays are independent, including bypasses and OCR input. Caller image and options remain unchanged.
- All nine public defaults unchanged: median/3, CLAHE, Otsu, global 127, adaptive block 31/C 11, morphology none/kernel 2. Fixed CLAHE settings 2.0/8x8 and selected Otsu cutoff returned as JSON-safe parameters alongside morphology/polarity/shape details. Unknown option keys, invalid method names, wrong image arrays, invalid integers/booleans and nonfinite numeric values fail clearly, even for bypassed settings. No contract change requested.
- Morphology uses inverted white text foreground, rectangular kernel, one iteration, anchor `(k//2,k//2)`, neutral constant borders, then restores dark-text/light-background convention. Even size 2 is allowed by contract and is asymmetric; known tests verify its anchor, border behavior, polarity and grayscale min/max. No automatic polarity guessing or hidden thresholding. Default morphology stays bypassed.
- Teaching/key functions/settings/actual measurements recorded in `docs/sprint_notes/SG03.md`. Covered cutoff example, Otsu within-group variance, Gaussian local threshold, structuring element, numeric 5x5 → 3x3/7x7 erosion/dilation, opening/closing order, thin-stroke damage, inversion and even-kernel shifts.
- Experiments: independent thresholds on common grayscale; independent erosion/dilation/opening/closing on its Otsu result; separate contract-default pipeline. All eight fictional samples unchanged at 1400x1000. Saved **72 measured rows, 72 alternative PNGs, 48 stage PNGs, 32 figures, 2 tables = 154 SG03 files**. Metadata includes hashes, versions, exact settings, dimensions/dtypes, binary flags and actual dark-pixel counts. Dark count uses intensity <128 on the whole page (including borders), not OCR accuracy. No exhaustive dataset parameter search.
- Visual inspection: eight figures listed exactly in SG03 notes (clear-income full thresholds/morphology detail; faint-income full/detail thresholds; noisy-caste threshold/morphology details; blurred-marksheet threshold/morphology details). Global 127 erased the faint page (0 dark pixels), Otsu selected 218 and retained text (63888 dark pixels). Noisy-caste Otsu selected 150 (64016 dark pixels) while adaptive produced heavy speckle (245721). Erosion weakens/breaks thin strokes; dilation thickens letters; 2x2 opening/closing have smaller geometric changes. Only listed figures visually inspected by assistant; all figures decode in tests; no human review or OCR improvement claimed.
- Changed files: `modules/preprocessing.py`, `scripts/run_experiments.py`, `tests/test_preprocessing.py`, `docs/sprint_notes/SG03.md`, `SAKSHI_HANDOFF.md`; `outputs/experiments/SG03/**`, `outputs/experiments/SG03_environment.json`, `outputs/experiments/SG03_tests.txt`, `outputs/experiments/SG03_reproducibility.json`. Dataset, SG01/SG02 evidence, shared files and peer paths untouched.
- Executed commands / actual results (from this checkout):
  - `git status --short --branch`, `git worktree list --porcelain`, `git log -4 --format='%H %an <%ae> %s'`: correct owner worktree/branch and SG02 commit, clean starting state.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json outputs/experiments/SG03_environment.json`: PASS; independent venv, Python 3.12.3, all six imports, Tesseract 5.3.4 with eng/osd. Environment evidence only.
  - Existing suite after code implementation: **15 PASS**. Initial new focused run: **9 functional checks PASS, artifact audit ERROR** because generation was still running. Generation then finished; sequential rerun resolved the missing-file error. Final full suite: **25 PASS**, including all regression/SG03 numerical, validation, polarity, contract and saved-artifact checks.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/run_experiments.py --sprint SG03`: PASS, 72 rows / 8 pipelines. Every saved alternative and stage recomputed/compared by audit; all source/output hashes and measured counts checked; all 32 figure files verified.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/run_experiments.py --sprint SG03 --output-dir /tmp/dip042-sg03-reproduce`: PASS. Python SHA256/file-set comparison: **154/154 files byte-identical**.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/run_experiments.py --sprint SG02 --output-dir /tmp/dip042-sg03-sg02-regression`: PASS. Comparison: **74/74 existing SG02 files byte-identical**. Both commands, directories and full hash maps saved in `outputs/experiments/SG03_reproducibility.json`.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python -m unittest discover -s tests -p test_preprocessing.py -v > outputs/experiments/SG03_tests.txt 2>&1`: final **25 tests PASS** (exit 0). Tiny-image combinations exercise 180 API configurations, not a dataset parameter search.
  - `.venv/bin/python -m compileall -q modules/preprocessing.py scripts/run_experiments.py tests/test_preprocessing.py`: PASS. `git diff --check`: PASS.
- Git identity: `extensions.worktreeConfig=true` already existed. Initial sandbox write to worktree Git config returned read-only filesystem; authorized retry succeeded. `git config --worktree user.name 'Sakshi Gupta'` and `git config --worktree user.email 'guptasak06@gmail.com'` set identity in `.git/worktrees/sakshi/config.worktree` only; shared/global identity unchanged. `git var GIT_AUTHOR_IDENT` confirmed Sakshi Gupta <guptasak06@gmail.com>.
- Local commit policy: this completion record is included with the verified sprint in the local commit **`SG03: Add validated thresholding, morphology and the contract pipeline`**. Resolve its hash using `git log -1 --format='%H %an <%ae> %s'`; check final working state with `git status --short --branch`. No push, publication, branch switch, main update or integration merge. Earlier start/checkpoint states are historical.
- Acceptance still unmet / unresolved errors / student-only actions: **none for SG03**. No peer/dependency request. Readiness/authenticity/eligibility claims unchanged; no real OCR/CER or end-to-end success claimed.
- Exact next action in a new chat: `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md and execute SG04. Verify the work and update the handoff before stopping.`
- Merge readiness: **SG03 complete locally; NOT READY for M01** until SG04 and peer build prerequisites pass. Merged at: **not yet**. Stop after SG03.

### SG04 start — 2026-11-10 13:40 Asia/Kolkata — session 1
- TODO → IN_PROGRESS. Read project rules, master, brief, contract-v1, own live handoff and M00 evidence. Latest user local-commit policy takes precedence over stale publication text in this checkout.
- Checkout `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi`, branch `codex/sakshi-dip`; clean start; SG03 prerequisite HEAD `704799ff2a783d2a444e631d4b31c35d8bbe69c4`; actual SG01/SG02 history present. No merge or branch switch.
- Explained OCR/system executable/PSM6 and CER with an edit-count example before coding. Plan: exact OCR API, blank/setup/timeout tests, known CER examples, hash-verified eight-sample real comparisons, raw texts/settings/errors, documented fixed default, teaching notes, final verification and Sakshi-authored local commit.
- Only owned files will change. No blocker or dependency/peer request. SG05 and M01 are out of this chat's scope.

### SG04 checkpoint — 2026-11-10 13:44 Asia/Kolkata — session 1
- Exact contract-v1 OCR wrapper implemented. BGR→RGB conversion, independent grayscale copy, raw-text preservation, explicit error/no_text/ok states. Confidence intentionally null (single text call, not an accuracy estimate). Inputs/config validation raises ValueError; engine failures return structured error. No UI/reference/test imports in production OCR module.
- Own environment PASS: Tesseract 5.3.4 and eng/osd available. Initial real dataset run PASS: 8 hash-verified/previously visually reviewed samples × 4 fixed methods = 32 actual OCR runs, all status ok, all normalized CER 0. Original has the same CER as processed methods; no measured improvement or general accuracy claim.
- Initial full suite: 43 tests PASS, including 5 actual Tesseract acceptance/error checks; artifact audit recomputes texts/metrics/images/settings and prior DIP checks remain passing. A ResourceWarning in the CSV audit was corrected with a context manager. Review also found the version probe could discard saved engine errors; now catches its setup failure, with a regression case. Final rerun pending these small corrections.
- Selected demo default remains contract-v1 median3→CLAHE2.0/8x8→Otsu→no morphology, processed OCR/eng/PSM6/20s. All fixed candidates tied on these easy related synthetic pages, so no evidence justifies changing the frozen default. Preserve manual original/grayscale alternatives; no reference-driven automatic upload selection.
- Remaining: regenerate final report metadata, reproducibility run, final suite/syntax/diff checks, teaching notes/completion and local owner-authored commit. No shared/peer edits, blocker or dependency request; no integrated application claim.

### SG04 completion — 2026-11-10 13:48 Asia/Kolkata — session 1
- Status: TODO → IN_PROGRESS → **DONE**. SG01–SG04 build package **READY FOR M01**, **not merged**. SG05/SG06 remain TODO and gated; stop after SG04.
- Checkout / branch / starting tip: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi` / `codex/sakshi-dip` / SG03 `704799ff2a783d2a444e631d4b31c35d8bbe69c4`. Actual SG01 `6629e0f`, SG02 `f4e0a36`, M00 `464c884` inspected. Clean starting worktree; no user edits overwritten, branch switch or merge.
- Implemented exact `extract_text(image, lang="eng", psm=6, timeout=20)` in `modules/ocr.py`. Accepts nonempty BGR/grayscale uint8, converts BGR→RGB, copies gray, preserves caller input and raw text. Exact keys `text/status/confidence/error/engine_config`; ok requires an alphanumeric character; successful blank/punctuation output is no_text. Missing executable/language data, OCR failures, timeouts and I/O errors produce structured error with explanatory diagnostic. Invalid input/config raises ValueError. PSM text modes 1 and 3–13 supported; 0/2 rejected explicitly. No production stub/reference data or UI import.
- Confidence is intentionally `None`: not measured, not accuracy. One Pytesseract text subprocess per call; timeout is finite positive seconds. Installed source was inspected for call/color/error behavior. No package/dependency/contract-default change.
- Added runner utilities `normalize_ocr_text`, `levenshtein_distance`, `character_error_rate`, fixed `compare_sg04`, reference/hash verification and `--sprint SG04`. Normalization: Unicode casefold, collapse all whitespace to a single space, trim; preserve punctuation/numbers; no correction. CER = minimum unit-cost edits / normalized reference characters; can exceed 1; empty reference (including empty/empty) raises ValueError, empty hypothesis/nonempty reference scores 1. Raw OCR remains separate. Error rows have null metrics and are saved before a failing CLI exit; version-probe setup errors cannot discard diagnostics.
- Real dataset evidence: 8 fictional source images, 4 fixed methods = **32 real Tesseract calls**, all `ok`, all normalized **CER 0**. Each method: 0 edits / **2190 reference characters**, mean CER 0 and pooled CER 0. Methods: original BGR, grayscale, contract-default processed, grayscale→Otsu (denoise/contrast none). Source/reference hashes match manifest and SG01 assistant visual review; no new student/human review. The simple synthetic derivatives share reference text and layout; normalization ignores case/spacing. **No measured preprocessing improvement, general OCR accuracy or integrated end-to-end success claimed.**
- Selected demo default: retain contract-v1 **median3 → CLAHE clip2.0/8×8 → Otsu → no morphology**, processed OCR with eng/PSM6/20s. All measured candidates tied, so no evidence justifies changing public defaults. Preserve original/grayscale/manual original-vs-processed selection at M01. No per-upload ground-truth selection. SG03 destructive demonstrations are not automatically chained into OCR.
- Teaching and key function explanations: `docs/sprint_notes/SG04.md`, including executable role, segmentation, channel order, status handling, CER examples/limits, actual per-sample table and reproduction commands. Actual raw clear-income original and blurred-marksheet default text inspected; all stored metrics/processed images audited numerically. No new page-by-page visual or human review claimed.
- Changed owned files: `modules/ocr.py`; `scripts/run_experiments.py`; `tests/test_ocr.py`; `tests/test_metrics.py`; `docs/sprint_notes/SG04.md`; this `SAKSHI_HANDOFF.md`; `outputs/experiments/SG04/**`, `SG04_environment.json`, `SG04_run.txt`, `SG04_tests.txt`, `SG04_reproducibility.json`. No edits to preprocessing/dataset, SG01–SG03 artifacts, peer code/handoff, shared master/merge/contract/requirements or main.
- Artifact directory `outputs/experiments/SG04/`: **66 files** = 32 raw OCR `.txt`, 8 normalized reference `.txt`, 24 processed PNGs, `metrics.csv`, `metrics.json`. JSON has actual raw OCR/result statuses/config, normalized comparison copies, edit counts, per-method summaries, all source/reference/processed/text hashes, array dimensions and versions. Originals refer to `dataset/`; references are `dataset/references/*.txt`; manifest/review `dataset/manifest.json` and `dataset/visual_review.json` unchanged.
- Commands / actual final results, all from this checkout:
  - `git status --short --branch`, `git worktree list --porcelain`, `git log -4 --format='%H %an <%ae> %s'`: PASS, correct owner/worktree/prerequisites and clean start; historical master snapshot not used as proof.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json outputs/experiments/SG04_environment.json`: PASS; own Python 3.12.3 venv, all 6 imports; Tesseract 5.3.4 with eng/osd. No install needed.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/run_experiments.py --sprint SG04 > outputs/experiments/SG04_run.txt 2>&1`: PASS, exit 0, 32 real comparisons. Regenerated after diagnostic metadata fix; final log/report retained.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python -m unittest discover -s tests -v > outputs/experiments/SG04_tests.txt 2>&1`: final **43 tests PASS** (5.750s, exit 0, no warnings). Includes 25 prior loading/DIP/reference checks, 11 OCR tests and 7 metric/artifact checks. Five OCR tests invoke the actual executable: clear title/name, white-page no_text, nonexistent executable, absent language data and enforced timeout. Mock checks are tests only. CER insertion/deletion/substitution/empty/>1 examples, changed-reference rejection, failure/null-score persistence, BGR/copy/parameter behavior and saved-output hashes/images/metrics/CSV/summaries also pass.
  - Initial suite also passed 43; its CSV-handle ResourceWarning was fixed. Review-found version-error persistence gap was fixed and regression-tested. Neither issue remains.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/run_experiments.py --sprint SG04 --output-dir /tmp/dip042-sg04-reproduce > /tmp/dip042-sg04-reproduce-run.txt 2>&1`: PASS, exit 0; independent repeat of all 32 real OCR calls. Relative-file-set/SHA256 comparison **66/66 files byte-identical**. Saved full comparison/hash maps and command in `outputs/experiments/SG04_reproducibility.json`.
  - `.venv/bin/python -m compileall -q modules/ocr.py scripts/run_experiments.py tests/test_ocr.py tests/test_metrics.py`: PASS. `git diff --check`: PASS. Existing SG02/SG03 image/metric artifacts recomputed/audited in the regression suite, unchanged.
  - `git config --worktree --get user.name`, `git config --worktree --get user.email`, `git var GIT_AUTHOR_IDENT`: PASS, existing worktree-specific **Sakshi Gupta <guptasak06@gmail.com>**. No shared/global identity edit.
- Local commit policy: include all reviewed SG04 owned code/evidence/notes and this completion record in one local commit with subject **`SG04: Add real Tesseract OCR and verified preliminary CER comparisons`**. Resolve resulting tip with `git log -1 --format='%H %an <%ae> %s'`, verify clean status. No push/publication/main update/integration merge; SG01 published history preserved. This record is written before creating its containing commit; the completion commit is identified by the subject and post-commit Git log, not a self-referential hash.
- Acceptance still unmet / unresolved error / student-only action: **none for SG04**. Requested peer/dependency/contract changes: **none**. M01 must still verify real UI flow and peer prerequisites separately; confidence-null and explicit error propagation match v1.
- Exact next action in a new merge chat: `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/MERGE_HANDOFF.md and execute the next eligible merge checkpoint. Verify both live build handoffs and actual branch tips first.`
- Next personal action only **after M01 passes and synchronizes**: execute SG05 from this checkout's handoff, with actual `docs/merge/M01.md` and real peer modules present. No SG05 started here. **Merged at: not yet.**
- Staging verification: first sandboxed `git add` could not create the linked-worktree index lock (read-only Git metadata). The authorized elevated retry succeeded. Reviewed **76 staged files**, all Sakshi-owned SG04 code/notes/evidence; `git diff --cached --check` PASS. This is a filesystem sandbox retry, not a test failure or automatic-review rejection. No code changed after the final passing suite/reproduction.
- Final local command: `git commit -m 'SG04: Add real Tesseract OCR and verified preliminary CER comparisons'`, followed by `git log -1 --format='%H %an <%ae> %s'` and `git status --short --branch`. The commit contains this record; use the resulting Git log as the authoritative hash/author and final response as the post-commit result.

### M01 integration annotation — 2026-11-10 14:36 Asia/Kolkata
- SG01–SG04 source cutoff `93a07b1` merged through normal history-preserving M01 merges (`8951039` Sakshi, `a8a0208` Jigisha). Earlier not-merged statements are historical.
- Full combined suite 101 PASS; real four-sample production smoke and two-upload browser flow PASS; downloads verified. `docs/merge/M01.md` records exact evidence, commands and limitations. No public contract/default/dependency change or fixture in the production flow.
- Only app notice/setup-error wording changed at integration; module behavior preserved. Recursive filesystem watching overflowed with nested worktrees; tested launch uses `--server.fileWatcherType=none`, requiring server restart after source changes.
- Synchronization pending into both clean personal checkouts; do not start SG05 until the completion annotation below. No SG05, human review or final evidence freeze performed. All commits local; main unchanged.

### M01 synchronization completion — 2026-11-10 14:40 Asia/Kolkata
- M01 DONE. This branch fast-forwarded to verified code/evidence `c1c155d5ab9368f13ede5781470ff4cc0673d38a` using `git merge --ff-only codex/integration`; all three tips matched and worktrees were clean. All real modules now physically present here. Own .venv imports/config validation and pip check PASS; correct owner Git identity retained.
- SG01–SG04 are DONE and merged at M01. SG05 remains TODO and is now the next eligible personal sprint. Use this checkout, not the root snapshot. Read `docs/merge/M01.md` and its real OCR/browser evidence before validation; final metrics/scenario evidence remains your sprint, then M02.
- Completion metadata is synchronized through a subsequent fast-forward before the merge chat stops; actual final tip is `git rev-parse HEAD`. Do not start from the older unmerged source cutoff. No API/default/dependency revisions, pending peer requests or required M01 user action. Local-only commits; main still deferred through M03.

### SG05 start — 2026-11-10 15:00 Asia/Kolkata — session 1
- TODO → IN_PROGRESS. Read AGENTS/master/brief/contract/own handoff and M00/M01 evidence; actual integrated modules inspected.
- Checkout `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi`, branch `codex/sakshi-dip`, clean initial state; HEAD and integration both `183ff6bfa6e67e2156eafc282044eb151e07ad39`. `git merge --ff-only codex/integration`: already up to date. Worktree-specific author is Sakshi Gupta <guptasak06@gmail.com>.
- Teaching before implementation: separate CER from rule correctness and checklist readiness; fixed independent DIP alternatives, no ground-truth selection in production. Plan hash-verified references, 14 fixed methods covering all seven comparisons, real full-app dataset evaluation, saved raw/normalized texts/settings/tables/figures, honest failure attribution, reproducibility and regression verification.
- Only Sakshi-owned files/evidence will change. No peer/shared files, dependencies, public defaults, main, pushes or later sprint/gate. No blocker or peer request at start.

### SG05 checkpoint — 2026-11-10 15:06 Asia/Kolkata — session 1
- Own environment/pip check PASS. Real first full run: 112 method OCR calls plus 16 calls through unchanged production `app.analyze_uploads`; eight samples, four source layouts. Default and original CER 0; correct types 8/8, present fields 28/28; 4 absent certificate-number slots stay None. Initial focused metric suite 13 PASS.
- Measured adverse results: global threshold erases faint income (no_text/CER 1); equalization and adaptive threshold damage noisy caste title; erosion changes `Application ID` to `Application 1D` (missed optional field); equalization misses blurred identity issue date. All are saved as observations, not patched by guessing values. No peer-owned defect identified.
- Reviewed first outputs and improved only SG05 evidence plumbing: proper two-panel original/default figure; alternative readiness records retain actual original OCR; non-field OCR errors are labeled explicitly; fixed M01 baseline provenance permits reproduction after evidence commits. Provisional first output moved to `/tmp/dip042-sg05-provisional-1509`, NOT final evidence. Final run regenerating into `outputs/experiments/SG05` with final runner/source hashes.
- Rechecked existing contact sheet against the four distinct raw transcripts; eight sample/reference hashes match unchanged SG01 visual review. Viewed final low-contrast threshold/original-default figures and noisy-caste early/morphology figures: expected blank/global, speckle/equalization and thin erosion strokes visible. No student/human review claimed.
- Remaining: finish final generation; rerun regression/audit; independent full reproduction; document final measured tables/limits/commands; mark READY FOR M02 and make local Sakshi-authored commit. No shared/peer edits, API/default changes, push or SG06.

### SG05 completion — 2026-11-10 15:11 Asia/Kolkata — session 1
- Status: TODO → IN_PROGRESS → **DONE**. **READY FOR M02** from Sakshi's side; **not merged or frozen**. SG06 remains TODO, waiting for M02. Stop after SG05; no JB05, merge checkpoint or report/slides executed.
- Checkout / branch / baseline: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi` / `codex/sakshi-dip` / `183ff6bfa6e67e2156eafc282044eb151e07ad39`. M01 code/worktree/environment inspected; clean start, `git merge --ff-only codex/integration` already up to date. No branch switch or integration merge.
- Implemented complete `scripts/evaluate_dataset.py`: 14 fixed methods cover all seven comparisons. Saves raw/normalized OCR/reference text, exact settings/contrast/histograms, image/text/source hashes, expected/observed type/fields, reference-only and expected-type rule diagnostics, per-file usability, explicit denominators and app reports. Rejects nonempty output destinations. No reference-driven production selection or fallback text.
- Ground truth: all eight image/reference hash pairs match manifest and unchanged SG01 `visual_review.json`. Opened existing contact sheet and compared four distinct raw transcripts; eight related samples retain four independent source layouts. No student/human verification claimed. All sources remain 1400×1000; no resize at max1800.
- Final measured run: **112 actual Tesseract calls** (8×14) plus **16 independent actual calls** through unchanged real `app.analyze_uploads` byte-input/original/processed/classification/extraction path. Tesseract5.3.4, eng, PSM6, timeout20; confidence null. No fixtures reported as OCR/integrated success.
- Original/default: both **0 edits / 2190 normalized reference characters**, pooled/mean CER0; correct types **8/8**, exact present fields **28/28**, absent certificate-number slots **4/4** separately. App observations match, all six stage array hashes checked. Full demonstration: 8 submitted files, 4 unique required types detected/usable, 100% coverage/readiness, Ready. Clear-only and degraded-only four-file subsets each have 4/4 usable; duplicates add no credit. Fictional names differ across types; cross-file applicant matching is outside this checklist.
- Honest adverse results: **7/112 nonzero-CER rows; 5/112 type/field-mismatch rows; 3 unknown type outcomes; 1 no_text; 0 engine/setup errors**. Global faint-income erases text (288/288 edits, CER1). Noisy-caste equalization:2436/295, CER8.257627119, unknown; adaptive:333/295, CER1.128813559, unknown. Erosion noisy-caste:1/295, Application ID→Application 1D, optional field missed. Equalized blurred-identity:5/244, issue date missed. Equalized blurred-marksheet:1/268 and global blurred-identity:2/244 change non-field text only. Complete method totals/settings are in validation/metrics; CER>1 is preserved.
- Reference-only classifier/extractor diagnostics pass expected values. Expected-type extraction on actual text is separately labeled. These checks are not OCR success counts or causal proofs. **No peer-owned defect established; peer/dependency requests: none.** Optional-field loss can leave configured readiness usable; noisy garbage can pass character-count readability. Limits recorded honestly.
- Default stays contract-v1 median3→CLAHE2.0/8×8→Otsu→no morphology, processed OCR. Original/default tie on this easy synthetic set; **no measured improvement, optimality, independent real-world accuracy or eligibility claim**. No production module/default/config/contract/dependency change. SG04 remains preliminary; SG05 supplies final measurement candidates pending M02 freeze. No earlier artifact invalidated.
- Owned changes: `scripts/evaluate_dataset.py`, `tests/test_metrics.py` (six new SG05 checks), `docs/validation/sakshi.md`, `docs/sprint_notes/SG05.md`, this handoff; `outputs/experiments/SG05/**`, `SG05_environment.json`, `SG05_run.txt`, `SG05_tests.txt`, `SG05_reproducibility.json`. No shared/master/merge/requirements/peer files changed. No production bug fix required.
- Final artifacts: **282 files** under `outputs/experiments/SG05/`: 112 raw OCR texts, 16 raw/normalized reference copies, 104 alternative PNGs, 40 figure PNGs, 10 report/table/index files. Tables: `metrics.json/.csv`, `summary.csv`, `original_processed.csv`. Real app evidence: `integrated_report.json/.md`, `integrated_observations.json`; checklist reports: `readiness_by_method.json`, `readiness_submissions.json`; inventory: `artifact_sha256.json`. Fingerprints cover real modules/app/config/contract/scripts; fixed M01 baseline remains reproducible after evidence commits.
- Visual review: existing contact sheet plus **8 final figures**: faint-income `thresholds.png`, `ocr_comparison.png`, `histograms.png`; noisy-caste `early.png`, `thresholds.png`, `morphology.png`; clear-income `early.png`; blurred-identity `early.png`. Saw white-out/global, noise amplification, erosion thinning and readable default; inspected layouts have no clipping/empty-panel issue. All 144 saved PNGs also decode/verify in audit; no visual review of every figure or human review claimed.
- Exact commands / actual final results (from this checkout):
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json outputs/experiments/SG05_environment.json`: PASS, own venv/Python3.12.3/all six imports/Tesseract5.3.4 eng+osd. `.venv/bin/python -m pip check`: PASS, no broken requirements. No installation.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/evaluate_dataset.py > outputs/experiments/SG05_run.txt 2>&1`: final PASS exit0, 112 method rows +8 production records, 128 actual calls. Initial provisional output moved to `/tmp/dip042-sg05-provisional-1509`; final evidence regenerated after SG05-only plumbing fixes in the checkpoint record.
  - Initial focused metric suite **13 PASS**. Final `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python -m unittest discover -s tests -v > outputs/experiments/SG05_tests.txt 2>&1`: **107 PASS**, 10.549s, exit0. Includes prior regressions, six SG05 checks, real OCR acceptance/error checks and peer's labeled fixture/AppTest checks. Bare-mode ScriptRunContext warnings are harness messages, not OCR failures. Audit recomputes arrays, metrics, rules, summaries, CSV, hashes and readiness; this is not 112 fresh OCR calls.
  - `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/evaluate_dataset.py --output-dir /tmp/dip042-sg05-reproduce-20261110 > /tmp/dip042-sg05-reproduce-run.txt 2>&1`: PASS exit0, repeats all 128 actual calls. Full file-set/SHA256 comparison **282/282 byte-identical**. Both maps/command saved in `outputs/experiments/SG05_reproducibility.json`.
  - `.venv/bin/python -m compileall -q scripts/evaluate_dataset.py tests/test_metrics.py`: PASS. `git diff --check`: PASS. No source changed after final suite/repeat; only completion docs. A completion-doc helper initially had an unterminated-string SyntaxError before any writes; corrected and rerun, without changing code/evidence or verification results.
- Git: worktree-specific Sakshi Gupta <guptasak06@gmail.com> verified; shared/global author unchanged. Local completion commit subject: **`SG05: Verify integrated dataset and reproducible final DIP OCR measurements`**. This record precedes its containing commit; obtain hash/author with `git log -1 --format='%H %an <%ae> %s'` and final state with `git status --short --branch`. No push/main update/publication/history rewrite; published SG01 preserved.
- Acceptance still unmet / unresolved error / student-only action: **none for SG05**. M02 must verify live peer JB05 readiness, combine browser evidence and recheck source fingerprints before freeze. This chat does not assert JB05 completion.
- Exact next action in a new merge chat: `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/MERGE_HANDOFF.md and execute the next eligible merge checkpoint. Verify both live validation handoffs and actual branch tips first.` If JB05 is incomplete, wait for **JB05** at `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha/JIGISHA_HANDOFF.md`. Do not merge incomplete validation work.
- Next personal action only after M02 passes and synchronizes: `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md and execute SG06. Verify the work and update the handoff before stopping.`
