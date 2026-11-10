# Sakshi Gupta — Personal sprint handoff

> A new chat receiving this file's path must execute **Sakshi's next eligible SG sprint only**, update this handoff in her own checkout, and stop. Do not start Jigisha's work or a merge automatically.

## Current position

- Owner: **Sakshi Gupta**.
- Role: image dataset, DIP pipeline, OCR, experiments, academic report; integration lead in separate M chats.
- Updated: 2026-11-10 13:21 Asia/Kolkata; **SG02 DONE locally**, verified; not merged.
- Active sprint: none; **SG02 completed**.
- Next: **SG03 — eligible; SG02 DONE**. Execute in a new chat using this handoff.
- Checkout: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi`. Branch: `codex/sakshi-dip`.
- GitHub repository: `https://github.com/guptasakshi06/Graphia`; shared remote `origin`; matching remote branch `origin/codex/sakshi-dip`. Initial M00 history published by user request; further pushes require user instructions.
- M00 baseline: single root commit named `M00` (resolve with `git rev-list --max-parents=0 HEAD`). The user requested one commit instead of three intermediate setup commits. Verified local `.venv`: Python 3.12.3; all six imports, `pip check`, Streamlit CLI and Tesseract 5.3.4 (`eng`, `osd`) PASS. Evidence: `docs/merge/M00-environment-sakshi.json` and `docs/merge/M00-environment-comparison.json`. Code/dependencies are unchanged by the history cleanup.
- Code/evidence merged: none.
- Peer requests: none.

Before M00 use the root `MERGE_HANDOFF.md` for shared setup. After M00 use **this file in Sakshi's checkout**, not a stale root copy. Read `HANDOFF.md`, `PROJECT_BRIEF.md`, `TEAM_CONTRACT.md` and `AGENTS.md` first. Contract APIs are fixed across tracks. Keep your own handoff current; do not change the master, Jigisha's handoff, or shared dependencies during parallel work.

## Sprint ledger

| Sprint | Day | Target | Depends on | Status | Integrated at |
|---|---|---:|---|---|---|
| SG01 | 1 | 60 min | M00 | DONE | Not merged; target M01 |
| SG02 | 1 | 75 min | SG01 | DONE | Not merged; target M01 |
| SG03 | 1 | 75 min | SG02 | TODO | Not merged; target M01 |
| SG04 | 1 | 75 min | SG03 | TODO | Not merged; target M01 |
| SG05 | 2 | 75 min | SG04, M01 | TODO | Not merged; target M02 |
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
