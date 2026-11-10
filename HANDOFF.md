# Project 042 — Two-person master handoff

> Planning revision: the previous sequential S01–S10 plan is superseded by the owner-specific SG/JB sprints and M merge checkpoints below. No implementation sprint from the old plan was started or completed.

## 1. Read this first

- **Project:** Document Intelligence for Application Readiness and Missing-Requirement Detection.
- **Person 1:** Sakshi Gupta — DIP, image dataset, OCR, experiments, academic report.
- **Person 2:** Jigisha Baiswar — rule-based classification, field extraction, checklist/readiness, Streamlit, presentation/viva.
- **Integration lead:** Sakshi Gupta; Jigisha reviews the application and presentation. A merge chat performs the concrete integration work, rather than asking either person to manually combine code snippets.
- **Planning date:** 2026-11-10, Asia/Kolkata. Update local timestamps during actual work.
- **Workspace/integration checkout:** `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi`.
- **Current phase:** **M00 DONE**. Tested setup, contract v1 and isolated workspaces synchronized. No application or dataset implementation started.
- **Next shared action:** M01 after Sakshi SG01–SG04 and Jigisha JB01–JB04 are DONE/READY; all are currently TODO.
- **Next Sakshi action:** SG01, now eligible in Sakshi's checkout.
- **Next Jigisha action:** JB01, now eligible in Jigisha's checkout. SG01 and JB01 can proceed independently at the same time.
- **Original full requirements:** `PROJECT_BRIEF.md`, preserved without edits.
- **Time budget:** Two focused days. Work estimates are targets, not calendar deadlines.

### Which file to give a new chat

| Purpose | Handoff | What a path-only request means |
|---|---|---|
| Shared setup, merge, or project-wide continuation | `MERGE_HANDOFF.md` or this file | Execute the next eligible M checkpoint; if waiting for a person, report that dependency |
| Sakshi's work | `SAKSHI_HANDOFF.md` | Execute the next eligible SG sprint only |
| Jigisha's work | `JIGISHA_HANDOFF.md` | Execute the next eligible JB sprint only |
| Shared APIs and data formats | `TEAM_CONTRACT.md` | Reference specification, not an implementation request by itself |

M00 created isolated checkouts at the paths below. The personal files in this root are integration snapshots. Give each new personal chat its **own checkout's handoff path**, so its status changes are saved on the correct branch. Actual paths:

```text
Sakshi: /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md
Jigisha: /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha/JIGISHA_HANDOFF.md
Merge: /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/MERGE_HANDOFF.md
```

Both worktree paths exist and their independent environments have been verified on this machine. On separate computers use separate copies/clones through a real transfer route and verify each local environment; a path alone cannot transfer files. User-requested remote: `origin` → `https://github.com/guptasakshi06/Graphia.git`. Initial M00 history is published on `main` and all three codex branches. Later pushes still require user instructions.

## 2. Work and status rules

1. One sprint or merge checkpoint per chat. Read `AGENTS.md`, this file, the selected personal/merge handoff, `TEAM_CONTRACT.md`, and relevant code first. Do not regenerate the whole project.
2. Resume the selected track's unfinished sprint before starting another. Follow its dependency gates; do not switch to the other person's tasks just because that person is ahead or behind.
3. Explain what/why/how/expected output before each implementation checkpoint, then provide complete working files, explain important functions/parameters, and verify each checkpoint before advancing. Teach in simple English with numerical DIP examples where useful.
4. Run available commands yourself. If a user-only terminal step or genuinely missing input is required, record the exact action and wait for its result. If the student asks to run every step personally, respect that pacing within the same sprint.
5. Preserve existing student work. Use local virtual environments and Ubuntu-specific setup. Test before claiming success. Imports alone do not prove OCR or the browser flow.
6. **Concurrent writers must not edit the same file.** Sakshi updates only her handoff/owned files; Jigisha updates only hers. During parallel work, do not update this master or the merge handoff. The integration chat reconciles them at M checkpoints.
7. Personal handoffs are authoritative for their live track status. This master is an explicitly dated integration snapshot, not a real-time shared tracker. Cross-check branch/worktree handoffs before reporting someone else's progress.
8. Personal agents may read peer files and use reviewed fixtures but must not change them. Record requested cross-owner changes in their own handoff. The merge chat resolves these requests concretely.
9. Freeze public interfaces in `TEAM_CONTRACT.md` at M00. Any later incompatible change requires a documented contract version change and both callers updated at a merge gate. Do not silently rename functions or keys.
10. Stop after the selected sprint. Before the final reply, update its ledger, verification evidence, remaining tasks, exact next command, branch/commit/working path, and own notes. Do not claim a separate merge, student review, or live viva has occurred.

**Statuses:** TODO, IN_PROGRESS, AWAITING_USER, BLOCKED, DONE, SKIPPED_OPTIONAL. DONE means acceptance checks have actual evidence. A completed personal sprint does not mean it is merged. Track merge state separately.

## 3. Ownership — separate files, separate work

| Files/area | Sole development owner |
|---|---|
| `modules/preprocessing.py`, `modules/ocr.py` | Sakshi |
| `dataset/**`, `scripts/create_sample_dataset.py`, `scripts/run_experiments.py`, `scripts/evaluate_dataset.py` | Sakshi |
| `tests/test_preprocessing.py`, `tests/test_ocr.py`, `tests/test_metrics.py` | Sakshi |
| `outputs/experiments/**`, `docs/validation/sakshi.md` | Sakshi |
| `docs/project_report.md`, final report DOCX/PDF, `docs/report_assets/**`, `docs/viva_sakshi.md` | Sakshi |
| `SAKSHI_HANDOFF.md`, `docs/sprint_notes/SG*.md` | Sakshi |
| `modules/classification.py`, `modules/extraction.py`, `modules/readiness.py` | Jigisha |
| `config/requirements.json`, `app.py` | Jigisha |
| `tests/fixtures/rule_cases.json`, `tests/test_classification.py`, `tests/test_extraction.py`, `tests/test_readiness.py`, `tests/test_ui.py` (if useful) | Jigisha |
| `outputs/screenshots/**`, `outputs/reports/**`, `docs/validation/jigisha.md` | Jigisha |
| `docs/diagrams/**`, `docs/presentation_outline.md`, presentation PPTX, `docs/viva_jigisha.md`, `docs/demo_script.md` | Jigisha |
| `JIGISHA_HANDOFF.md`, `docs/sprint_notes/JB*.md` | Jigisha |
| `AGENTS.md`, `HANDOFF.md`, `MERGE_HANDOFF.md`, `TEAM_CONTRACT.md`, `requirements.txt`, `.gitignore`, `modules/__init__.py`, `README.md`, `scripts/check_environment.py`, `docs/merge/**`, final `docs/viva.md`, final delivery manifest | Integration chat, led by Sakshi |
| `PROJECT_BRIEF.md` | Read-only original requirements |

No shared experiment script or combined report file should be edited by both tracks. Request dependency changes through the personal handoff; only the integration lead edits `requirements.txt`. Every module remains plain Python, independently testable without Streamlit.

## 4. Parallel schedule and dependency gates

| Stage | Day | Sakshi Gupta | Jigisha Baiswar | Gate/elapsed target |
|---|---|---|---|---|
| Foundation | 1 | M00: shared environment/baseline as integration lead | Check own local environment using the baseline | 45–60 min; sequential foundation |
| Parallel build 1 | 1 | SG01: dataset + image input, 60 min | JB01: classification + text fixtures, 60 min | Both depend only on M00 |
| Parallel build 2 | 1 | SG02: grayscale/filter/contrast, 75 min | JB02: field extraction, 60 min | Within-track prerequisites |
| Parallel build 3 | 1 | SG03: threshold/morphology, 75 min | JB03: readiness + reports, 60 min | Within-track prerequisites |
| Parallel build 4 | 1 | SG04: OCR + initial CER, 75 min | JB04: UI with explicit contract adapters, 90 min | Own modules ready independently |
| Code merge | 2 | M01 integration lead | Review app behavior and own interfaces | 60–90 min; requires SG04 + JB04 |
| Parallel validation | 2 | SG05: real OCR evaluation + final measurements, 75 min | JB05: browser flows + screenshots, 75 min | Both start from M01 |
| Evidence merge | 2 | M02 integration lead | Review UI results | 30–45 min; requires SG05 + JB05 |
| Parallel submission | 2 | SG06: college report + DIP/OCR viva, 90 min | JB06: diagrams + PPTX + app viva/demo, 90 min | Both start from M02's frozen evidence |
| Final merge | 2 | M03 integration lead | Review slides and delivery | 30–45 min; requires SG06 + JB06 |

Target critical path: around 5.5–6 hours on Day 1 and 5–6 hours on Day 2, plus a buffer of up to an hour each day. Individual sprint durations are not promises. The workload is parallel, so do not add both people's hours as elapsed project time. Keep optional features out if buffers are consumed.

### Master status snapshot — M00 complete, 2026-11-10 12:46 Asia/Kolkata

| Track | Sprints/checkpoints | Status | Merged state |
|---|---|---|---|
| Shared setup | M00 | DONE | Single root commit `M00`; no personal code merged |
| Sakshi build | SG01, SG02, SG03, SG04 | All TODO | Not merged |
| Jigisha build | JB01, JB02, JB03, JB04 | All TODO | Not merged |
| Code integration | M01 | TODO | Waiting for both build tracks |
| Sakshi validation | SG05 | TODO | Not merged |
| Jigisha validation | JB05 | TODO | Not merged |
| Evidence integration | M02 | TODO | Waiting for both validation tracks |
| Sakshi report | SG06 | TODO | Not merged |
| Jigisha slides/viva | JB06 | TODO | Not merged |
| Final integration | M03 | TODO | Waiting for both submission tracks |

Each M checkpoint has its own work order in `MERGE_HANDOFF.md`. Each SG/JB sprint has detailed tasks and acceptance checks in its personal handoff. M00 records the real checkout paths; M01/M02/M03 must record actual branch tips, checks and resolutions.

## 5. Minimum viable application and scope boundaries


### Required implementation

- Multiple JPG/JPEG/PNG uploads in one application submission; original image previews.
- Visible grayscale, denoising, contrast enhancement, three threshold methods, and four morphology demonstrations.
- Configurable preprocessing with intermediate results and clear parameters; compare alternatives instead of blindly chaining every transformation.
- Tesseract OCR on original and selected processed images, with both texts shown and a useful no-text/error state.
- Rule-based detection of Income Certificate, Caste Certificate, Marksheet, Identity Proof, or Unknown Document.
- Conservative regex extraction of fields that the actual sample layouts support. Candidate fields are student name, certificate number, application ID, and issue date. Not every field applies to every document.
- Configurable required document types and required fields, distinct submitted/missing/unreadable states, and transparent readiness calculation.
- A downloadable readiness report with counts, per-file details, extracted information, missing items, readability, and percentages.
- Approximately eight clearly labeled fictional or reusable sample documents, with clear, low-contrast, noisy, and slightly blurred conditions represented.
- Measured comparisons, screenshots, README, academic report, presentation, architecture/workflow diagrams, and viva preparation.

### Optional; defer until all required work is complete

- PDF upload and page conversion (`pdf2image`/Poppler).
- Deskew, perspective correction, multilingual OCR, batch export formats beyond the simple report, Pandas, decorative UI work, and extra datasets.
- A live mock viva after materials are prepared. It must be interactive, one question at a time, when the student is available; never invent student answers.

### Excluded

Deep learning, TensorFlow/PyTorch, CNNs, transformers, LLM services, cloud deployment, databases, authentication, separate API servers, and authenticity or eligibility verification.

## 6. Common behavior requirements


- **Image convention:** OpenCV processing uses BGR `uint8` arrays; grayscale is a two-dimensional `uint8` array. Convert BGR to RGB for display. Decode Pillow/Streamlit input consistently, honor EXIF orientation, and normalize transparent images against white. Set a reasonable image size limit and record resize dimensions.
- **Type IDs:** `income_certificate`, `caste_certificate`, `marksheet`, `identity_proof`, `unknown`. Keep user-facing names separate. Use these same IDs in classification, configuration, reports, fixtures, and UI.
- **Preprocessing:** Return named intermediate images and parameters; do not modify the caller's original image. Distinguish demonstrated alternatives from the selected OCR pipeline. Kernel sizes must be valid and threshold parameters explained.
- **OCR result:** Keep extracted text, engine/config information, optional heuristic confidence, and explicit error/no-text states. Missing Tesseract is a setup error, not an empty successful result.
- **Classification:** Return the selected type plus matched keyword evidence. Ambiguous competing matches need conservative handling; prefer `unknown` with an explanation over an arbitrary confident answer. A keyword score is not calibrated probability.
- **Fields:** Retain raw OCR text. Return missing/uncertain fields explicitly, with reasons if practical. Match nearby labels instead of grabbing any number or line. Never invent a name, identifier, date, or field value. UI uses `Not Found / Unreadable` where OCR cannot distinguish the cause.
- **Per-file record:** Keep a stable ID, filename, type/evidence, OCR text/status, extracted fields, readable/unreadable assessment, and processing settings. Streamlit owns orchestration; analysis functions should be usable without importing Streamlit.
- **Configuration:** A local JSON file defines a clearly labeled demonstration scholarship checklist and per-type required fields. The UI may select required types for the current session. Do not present sample requirements as official scholarship rules.
- **Readability:** Define a documented, configurable heuristic based on actual usable OCR text and required-field extraction. OCR confidence may be supplementary; neither confidence nor character count proves accuracy. An unreadable but recognizable document remains present and is separately flagged unusable.
- **Counts:** `submitted_file_count` is all uploads; `detected_required_type_count` is unique required types recognized; `usable_required_type_count` is required types with at least one readable candidate meeting that type's configured required fields. Report these separately.
- **Percentages:** Document coverage = `100 × detected_required_type_count / required_type_count`; readiness = `100 × usable_required_type_count / required_type_count`. Duplicates never increase either percentage. Unknown/unrequired documents do not satisfy required types. A required type is usable only if at least one individual candidate meets all its requirements; never assemble fields from different students/documents.
- **Statuses:** Ready when all configured required types have a usable candidate; Needs Attention when all are detected but some are unusable; Incomplete when at least one required type is absent. Missing types and detected-but-unreadable types must be separate lists. Reject an empty checklist with a clear validation message instead of dividing by zero or showing 100%.
- **Claims:** Readiness describes this configured checklist only. Display that the system does not verify authenticity, official eligibility, or that different uploaded documents belong to the same person.
- **Exports:** Plain JSON and a readable text/Markdown report are sufficient. No PDF reporting dependency is needed for the app's MVP.

### DIP syllabus mapping


| Component | Concept the students must explain |
|---|---|
| Image reading/resizing | Pixel arrays, spatial resolution, interpolation, color channel order |
| Grayscale | Weighted intensity conversion and reduced channel count |
| Gaussian/median filtering | Smoothing, neighborhood processing, noise and detail tradeoffs |
| Histograms/equalization/CLAHE | Intensity distribution, global versus local contrast |
| Global/Otsu/adaptive thresholds | Segmentation, variance, local illumination |
| Morphology | Structuring elements and foreground geometry |
| OCR | Downstream recognition affected by preprocessing; Tesseract is external recognition software |
| Classification/extraction/readiness | Simple application logic built on OCR, not additional DIP algorithms |

## 7. Test and evidence rules

- Use focused standard-library tests/scripts where practical, not a large testing framework.
- Sakshi's measurements use actual images, real Tesseract outputs, and visually verified reference text. CER uses Levenshtein distance/reference length with a stated normalization; it may exceed 1. Confidence is not accuracy.
- Jigisha's initial known-text fixtures and fake OCR adapters are labeled test/development data. They prove rule/UI behavior only. Replace adapters with real functions at M01 and evaluate against real OCR at SG05/JB05.
- Approximately eight labeled fictional/reusable samples must cover four types and clear/low-contrast/noisy/slightly blurred conditions. Derivatives are not independent real-world samples. Never fabricate experiment numbers or screenshot results.
- All seven original comparison requirements remain mandatory: original/grayscale, original/enhanced, Gaussian/median, global/Otsu/adaptive, erosion/dilation, opening/closing, original/processed OCR.
- Missing required types, present-but-unreadable types, unknowns and duplicate uploads must be tested separately. Readiness is based on unique usable required types; coverage is distinct.
- Record exact executed commands, PASS/FAIL/NOT RUN, actual observed results and artifact paths. A planned command is not a passed check.
- Do not save private uploads by default. Do not push, deploy or send anything to others without a user request.

## 8. Submission tracker — integration updates only

| Deliverable | Owner/gate | Status | Verified path |
|---|---|---|---|
| Environment/dependencies/source organization | M00, M03 | M00 DONE; final audit at M03 | `requirements.txt`, `scripts/check_environment.py`, `docs/merge/M00*.json` |
| Dataset + references + provenance | SG01 | TODO | — |
| DIP pipeline + all comparisons | SG02–SG05 | TODO | — |
| OCR + measured results/raw outputs | SG04–SG05 | TODO | — |
| Classification/fields/readiness/report export | JB01–JB03 | TODO | — |
| Real integrated Streamlit application | JB04, M01, JB05 | TODO | — |
| Final experiment tables + screenshots | SG05, JB05, M02 | TODO | — |
| README | M03 | Starter setup guide written; final guide at M03 | `README.md` |
| Academic report, editable source + usable artifact | SG06 | TODO | — |
| Actual PowerPoint `.pptx` | JB06 | TODO | — |
| Architecture + workflow diagrams | JB06 | TODO | — |
| Combined viva Q&A and demo script | SG06, JB06, M03 | TODO | — |
| Interactive mock viva | Optional follow-up | NOT CONDUCTED | — |

## 9. Current environment and decisions

Observed at M00: Ubuntu 24.04.4 LTS, Python 3.12.3, root pip 26.3; three independent `.venv` environments with all six imports and dependency checks PASS. NumPy 2.5.4, OpenCV headless 5.0.0.93, Matplotlib 3.11.2, Pytesseract 0.3.13, Streamlit 1.67.0, Pillow 13.0.0. System Tesseract 5.3.4 with `eng`/`osd`. All 42 installed distributions match the recorded snapshot. No apt/sudo installation was needed. Evidence: `docs/merge/M00.md` and adjacent JSON files.

Current Git baseline: single root commit named `M00` (resolve with `git rev-list --max-parents=0 HEAD`). The user requested replacing the three intermediate setup commits with this single commit. Existing setup evidence remains valid: code and dependencies are unchanged. All three workspaces retain their codex branches; GitHub `main` points to the same M00 baseline. Repository: `https://github.com/guptasakshi06/Graphia`. No dataset, application module, app or server exists yet. A temporary setup-only OCR phrase was read successfully; this is not dataset accuracy or end-to-end application evidence.

| Decision | Reason |
|---|---|
| 2026-11-10: Replace sequential S01–S10 with SG/JB tracks and M gates | User requested separate work for Sakshi Gupta and Jigisha Baiswar, then merging |
| Separate branches and working directories | Concurrent Git checkouts and shared-file writes can corrupt each other's work |
| One owner per file; personal status lives in personal handoffs | Prevent merge conflicts in code and tracking documents |
| Contract-first rules/UI development | Jigisha need not wait for Sakshi's OCR implementation |
| Merge real code before final experiments and submission artifacts | Ensure all report/slide claims match the actual integrated application |

Open risks: system-install access was not needed or tested; no sample images are supplied yet; college/roll-number/faculty metadata and report format are unknown; two days is tight. Names **Sakshi Gupta** and **Jigisha Baiswar** are known and should appear accurately in final materials. Use placeholders only for missing metadata.

## 10. Handoff maintenance after every sprint

Personal agents update their own handoff, never the shared master during parallel work. Required fields: owner, sprint ID/status, actual timestamp, checkout/branch, changed files, concepts taught, exact checks/results, evidence paths, unresolved errors, requested peer changes, remaining work, local commit/diff state, next eligible sprint, merge readiness and merge state. Record clean/dirty state truthfully; do not commit unrelated changes.

Use `docs/sprint_notes/SGxx.md` or `JBxx.md` for teaching notes. A sprint may be code-complete but awaiting user-only verification; retain AWAITING_USER until evidence arrives. If all owned pre-merge work is done, stop and point to the M gate; do not implement the peer's tasks.

At each M gate the integration chat reads both live handoffs, merges owned work, updates this snapshot and submission tracker, updates `MERGE_HANDOFF.md`, and writes an immutable evidence summary under `docs/merge/`. Synchronize the integration branch into both tracks before their next parallel round. Record actual paths and commands so the student only needs the correct handoff path next time.

### History

- 2026-11-10: Original full brief preserved; initial sequential planning created. No implementation performed.
- 2026-11-10: User named both teammates and requested separate work followed by merges. Planning reorganized into two six-sprint personal tracks plus four shared checkpoints. All implementation statuses remain TODO.

- 2026-11-10 12:43 Asia/Kolkata: M00 root/worktree environments verified and contract v1 frozen. Initial local baseline `09893da4d1fea88d985baa12c0c77221c9750a4e`. Shared foundation synchronization pending; no personal sprint started.

- 2026-11-10 12:46 Asia/Kolkata: **M00 DONE**; common verified foundation `01b3e869f64a7c58f2c4aee31e0cd65cf25c1058` synchronized into both clean personal branches. Final completion metadata is documentation only. SG01/JB01 are independently eligible; M01 still waits for both build tracks.

- 2026-11-10 12:53 Asia/Kolkata: User-requested GitHub publication succeeded to `https://github.com/guptasakshi06/Graphia`. Original M00 tip `7cc5a4f` published atomically to `main`, `codex/integration`, `codex/sakshi-dip` and `codex/jigisha-app` without force. Repository was empty before publication. No new sprint executed. Remote setup guidance is included in the single M00 commit requested below.

- 2026-11-10 12:56 Asia/Kolkata: User explicitly requested removing the three previous GitHub commits and keeping one commit named **M00**. All setup/source/evidence files and repository guidance are retained in that single root commit. Historical entries above describe pre-squash setup; their hashes are not the current branch baseline. Future chats must use the current root M00 commit.
