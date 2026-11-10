# Jigisha Baiswar — Personal sprint handoff

> A new chat receiving this file's path must execute **Jigisha's next eligible JB sprint only**, update this handoff in her own checkout, and stop. Do not start Sakshi's work or a merge automatically.

## Current position

- Owner: **Jigisha Baiswar**.
- Role: rule-based classification, field extraction, readiness/report exports, Streamlit, screenshots, diagrams, slides and app viva/demo.
- Updated: 2026-11-10 12:46 Asia/Kolkata; **M00 DONE**, personal work not started.
- Active sprint: none.
- Next: **JB01 — eligible; M00 DONE**.
- Checkout: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha`. Branch: `codex/jigisha-app`.
- GitHub repository: `https://github.com/guptasakshi06/Graphia`; shared remote `origin`; matching remote branch `origin/codex/jigisha-app`. Initial M00 history published by user request; further pushes require user instructions.
- M00 baseline: single root commit named `M00` (resolve with `git rev-list --max-parents=0 HEAD`). The user requested one commit instead of three intermediate setup commits. Verified local `.venv`: Python 3.12.3; all six imports, `pip check`, Streamlit CLI and Tesseract 5.3.4 (`eng`, `osd`) PASS. Evidence: `docs/merge/M00-environment-jigisha.json` and `docs/merge/M00-environment-comparison.json`. Code/dependencies are unchanged by the history cleanup.
- Code/evidence merged: none.
- Peer requests: none.

Before M00 use the root `MERGE_HANDOFF.md` for shared setup. After M00 use **this file in Jigisha's checkout**, not a stale root copy. Read `HANDOFF.md`, `PROJECT_BRIEF.md`, `TEAM_CONTRACT.md` and `AGENTS.md` first. Keep your own handoff current; do not change the master, Sakshi's handoff, shared dependencies or her image/OCR modules during parallel work.

Your first four sprints must not wait for Sakshi's OCR. Use clearly labeled known-text fixtures and the fixed contract. Passing fixtures proves your rules, not real OCR accuracy. Real integration starts at M01.

## Sprint ledger

| Sprint | Day | Target | Depends on | Status | Integrated at |
|---|---|---:|---|---|---|
| JB01 | 1 | 60 min | M00 | TODO | Not merged; target M01 |
| JB02 | 1 | 60 min | JB01 | TODO | Not merged; target M01 |
| JB03 | 1 | 60 min | JB02 | TODO | Not merged; target M01 |
| JB04 | 1 | 90 min | JB03 | TODO | Not merged; target M01 |
| JB05 | 2 | 75 min | JB04, M01 | TODO | Not merged; target M02 |
| JB06 | 2 | 90 min | JB05, M02 | TODO | Not merged; target M03 |

## JB01 — Rule fixtures and document classification

**Build:** Independently testable keyword classification using agreed document types.

1. Verify Jigisha's checkout/branch and local `.venv` using M00 instructions. On a second machine install from the same requirements; do not assume Sakshi's system setup exists locally.
2. Explain normalized string matching, keyword evidence, ambiguity and why these rules are not trained ML.
3. Create `tests/fixtures/rule_cases.json` with clearly labeled fictional/reference OCR strings for four types, unrelated/blank text and mixed/ambiguous keywords. Include expected field values for JB02 and record that these are not measured OCR outputs.
4. Implement `classify_document(text)` in `modules/classification.py` exactly as contracted. Return type, evidence and ambiguity; preserve raw text and never use filenames.
5. Test all four known types, unknown, blank, case/whitespace variation, and conflicting cues. Conservative ambiguity is preferable to a forced incorrect type.

**Owned outputs:** Classifier, rule fixtures, `tests/test_classification.py`, `docs/sprint_notes/JB01.md`.

**Acceptance:** Five possible type outcomes work; evidence is inspectable; no dependency on image/OCR/Streamlit modules; empty/ambiguous cases are safe. Tests actually executed and results recorded.

**Handoff:** Record fixture vocabulary and known rule limits. Stop; next JB02.

## JB02 — Conservative selected-field extraction

**Build:** Simple label-aware regex for the agreed sample layouts.

1. Explain regex groups, nearby labels and why any arbitrary number cannot be assumed to be a certificate number.
2. Implement `extract_fields(text, doc_type)` in `modules/extraction.py` with the four contracted keys and string/None values. Use Student Name, Certificate Number, Application ID, Issue Date and carefully chosen variants from fixtures.
3. Keep identifiers as strings to preserve leading zeroes. Validate dates/formats conservatively without guessing ambiguous values. Not every field belongs on every type.
4. Test positive fixtures, blank/unknown text, missing labels, malformed dates/IDs and unrelated numbers. Missing fields remain None; display formatting happens later.
5. Document what layouts the regex supports and any uncertainty. If actual OCR is not available yet, explicitly defer robustness claims to SG05/JB05.

**Owned outputs:** Extraction module, fixture extensions, `tests/test_extraction.py`, JB02 notes.

**Acceptance:** Supported labeled fields extracted correctly on known text; unrelated digits not falsely extracted; absent/malformed values remain missing; no fabricated fallback names/IDs.

**Handoff:** Record required-field recommendations consistent with the shared contract. Stop; next JB03.

## JB03 — Checklist, readability, readiness and report exports

**Build:** Deterministic submission checking independent of OCR implementation.

1. Implement the demonstration `config/requirements.json` shape from the contract. All four types require a name; two certificate types also require their certificate number. Other extracted fields remain optional initially.
2. Explain the readability heuristic, unique-document-type counts and the difference between coverage and readiness. Do not describe the sample policy as official scholarship rules.
3. Implement `analyze_readiness` and `render_report` in `modules/readiness.py` exactly as contracted. Return per-file text/fields/problems and application-level counts/missing/unusable/status/percentages. Keep arrays out of JSON exports.
4. Build test document records using the contracted OCR result shape. Each type needs one individually readable candidate meeting every required field; do not combine fields from separate files or assume matching identity.
5. Verify complete, missing, unreadable, missing-field, unknown/unrequired, duplicate, one-good-one-bad-duplicate, empty-submission and empty-checklist cases. Reject invalid type/field/settings configuration.
6. Produce sample JSON and readable report exports under `outputs/reports/`, visibly labeled fixture-based until real integration.

**Owned outputs:** Readiness module, configuration, `tests/test_readiness.py`, sample report exports, JB03 notes.

**Acceptance:** 3 usable of 4 required = 75% readiness; 4 detected/3 usable = 100% coverage and 75% readiness; duplicates cannot inflate either; empty required selection rejected; missing versus detected-but-unusable lists separate. Tests run.

**Handoff:** Record report schema and actual edge-case outcomes. Stop; next JB04.

## JB04 — Streamlit interface against the fixed contract

**Build:** UI ready to connect to real DIP/OCR at M01, without blocking on Sakshi's branch.

1. Implement `app.py`: project/dashboard instructions, multi-image JPG/JPEG/PNG uploads, configurable required type selection, per-file preview, named processing views, original/processed OCR display, detected type/fields, readiness and report downloads.
2. Use the exact public image/OCR APIs from `TEAM_CONTRACT.md`. Do not create competing preprocessing/OCR modules. If absent, defer imports until needed and show a clear missing-module message; use fixtures only through a clearly separate test/development adapter.
3. Keep fake providers under your tests or an explicitly development-only file. Do not silently fall back to fake OCR in the production path, and do not show a ready application report from fabricated upload text.
4. Add an explicit analyze action, stable IDs for same-name uploads, session state, invalidation when uploads/options/checklist/OCR source change, and per-file error handling.
5. Convert BGR to RGB only for display, use `.getvalue()` bytes for `load_image`, and classify/extract from the selected original/processed OCR consistently.
6. Test UI logic and fixture-driven interaction where possible; start Streamlit and inspect layout. Clearly state this is pre-integration until M01's real upload test. Do not spend time on decorative features.

**Owned outputs:** `app.py`, small clearly labeled test adapter if needed, focused UI checks, JB04 notes. Do not capture fixture screens as final experimental evidence.

**Acceptance:** UI starts; controls and report rendering work against the agreed schema; missing modules/errors are clear; session invalidation is checked; fake providers cannot masquerade as production processing. Real end-to-end behavior is intentionally reserved for M01/JB05.

**Handoff:** Mark READY FOR M01 with APIs used, adapter-removal checklist, commands/results, changed files, branch tip/diff and requested peer changes. Stop and provide the root merge handoff path. JB05 waits for M01 and the merged real modules.

## JB05 — Real browser verification and screenshots

**Build:** Evidence of the actual merged application's behavior.

1. Verify M01 merge record and synchronize your clean branch from integration. Confirm production code uses real Sakshi functions and Tesseract, not test adapters.
2. Run `.venv/bin/python -m streamlit run app.py` using your checkout's environment. In a browser upload real synthetic sample images from the merged dataset, first singly and then as a complete set.
3. Verify upload → intermediate images → original/processed OCR → type/fields → checklist → report download. Exercise missing document, recognized-but-unusable candidate, duplicate files including same filenames, unknown/blank/corrupt input, and changed settings/checklist.
4. Download and inspect real JSON/text reports. Check unique counts/percentages against actual expected scenarios. Record fixture-only cases separately if real samples cannot reliably trigger a particular state; never imply that such a case demonstrates actual OCR behavior.
5. Save real screenshots of dashboard, DIP views, OCR/fields, missing state and readiness/report. Use outputs from actual execution. Do not stage a fake success screenshot.
6. Fix your owned UI/rule bugs and rerun affected checks. Record Sakshi-owned requests locally for M02. Write `docs/validation/jigisha.md` with exact commands, scenarios and evidence.
7. If browser access is unavailable, provide the precise student test steps and keep affected acceptance items AWAITING_USER. Server startup alone is not a successful UI test.

**Owned outputs:** `outputs/screenshots/**`, real `outputs/reports/**`, Jigisha validation summary, owned code fixes, JB05 notes.

**Acceptance:** Full real flow verified; stale results invalidated; missing and unusable states separate; downloads accurate; screenshots traceable to runs; fake adapters absent from production. Record remaining issues honestly.

**Handoff:** Mark READY FOR M02 with artifacts and peer-change requests. Stop; JB06 requires frozen M02 evidence.

## JB06 — Diagrams, actual PowerPoint, app viva and demo

**Build:** Submission presentation and demonstration materials based on frozen evidence.

1. Verify M02 final measurements and UI outputs, then use only those claims and paths. Read merged actual architecture before diagramming.
2. Create architecture and workflow diagram sources plus rendered images at `docs/diagrams/architecture.png` and `docs/diagrams/workflow.png`. Include DIP stages, original/processed OCR, rules, fields, checklist, missing/unusable handling and reports. Sakshi's report will use these exact paths at M03.
3. Write `docs/presentation_outline.md` and a real `.pptx`, approximately 10–12 slides: problem/objectives, architecture/workflow, DIP stages, OCR, rules/fields/readiness, actual experiments/results, screenshots, limitations and conclusion/demo. Include both student names correctly.
4. Read/apply the available presentation skill/tools at execution time. Render slides and inspect text/figures for clipping/readability. An outline is not a completed PowerPoint.
5. Write `docs/viva_jigisha.md` covering classification keywords, regex, unknown/ambiguous cases, missing requirements, readability/coverage/readiness formulas, duplicate handling, UI state, authenticity/eligibility limits, and system limitations. Give simple natural answers.
6. Write `docs/demo_script.md`: launch commands, short sequence, Sakshi explaining DIP/OCR/experiments and Jigisha explaining rules/readiness/UI, known issues and recovery commands. Include a short cross-teaching checklist so both students understand the complete project.
7. Offer a follow-up mock viva only when the student is available, one question at a time. Preparing questions is not conducting it.

**Owned outputs:** Two diagrams with sources, slide outline + actual PPTX, app viva notes, demo script, JB06 notes.

**Acceptance:** Diagrams match implemented modules; slides open/render and use actual M02 numbers/screenshots; student names correct; limitations explicit; no invented features/results. All 14 final-deliverable categories in the original brief have an owner; M03 audits completeness.

**Handoff:** Mark READY FOR M03 with artifact paths and render evidence. Stop; do not claim final merge or submission.

## Update this handoff after every session

Update current position, own ledger, branch/path, active/next sprint, merge-readiness and peer requests. Append a record; never erase earlier evidence or edit the shared master while both tracks are active.

```markdown
### JBxx — YYYY-MM-DD HH:MM Asia/Kolkata — session N
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

2026-11-10: Personal track planned. All JB sprints TODO; no rules, UI, environment checks or merges performed.

### M00 foundation annotation — 2026-11-10 12:43 Asia/Kolkata
- This integration-session setup annotation does not execute a personal sprint. All personal sprint statuses remain TODO; no code/evidence has been merged at M01.
- Actual checkout/branch: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha` / `codex/jigisha-app`. Created from common setup baseline `09893da4d1fea88d985baa12c0c77221c9750a4e`.
- In this checkout: `python3 -m venv .venv` and `.venv/bin/python -m pip install --no-cache-dir --no-index --find-links /tmp/dip042-wheelhouse -r requirements.txt -c docs/merge/M00-requirements-lock.txt`: PASS. The /tmp wheel cache is local convenience only; future machines install from the package index.
- In this checkout: `MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/docs/merge/M00-environment-jigisha.json`: PASS; `.venv/bin/python -m pip check`: PASS; `.venv/bin/python -m streamlit --version`: PASS (1.67.0).
- Independent venv prefix verified; `.venv/bin/python -m pip freeze` matches all 42 distributions in the common M00 snapshot. System Tesseract is shared on this machine; Python environments are separate.
- Contract v1 frozen without signature/schema changes. No human walkthrough, dataset evaluation or application success claimed.
- Shared foundation record will be synchronized from integration before this sprint begins. Use only your own handoff after that sync; master/peer handoffs are snapshots.
- Next action after M00 DONE: read this handoff in this checkout and execute **JB01 only**. Do not implement the peer track or the next merge gate.

### M00 completed — 2026-11-10 12:46 Asia/Kolkata
- M00 DONE. Shared setup baseline `09893da4d1fea88d985baa12c0c77221c9750a4e`; verified foundation record `01b3e869f64a7c58f2c4aee31e0cd65cf25c1058` was forward-merged into this clean personal checkout using `git merge --ff-only codex/integration`.
- Own handoff, contract, requirements, environment checker and shared records were compared with integration after the sync: PASS. All environment checks above passed on this machine. Final completion metadata is documentation only and is synchronized before this chat ends.
- No personal sprint executed; all sprint ledger rows remain TODO; no personal code/evidence merged at M01. No open peer/dependency requests.
- Exact next action: in a new personal chat, request execution of **JB01 only** using `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha/JIGISHA_HANDOFF.md`. Work in this checkout and update this copy of the handoff. Do not edit the root/peer handoffs or shared requirements during personal work.

### GitHub setup annotation — 2026-11-10 12:53 Asia/Kolkata
- User requested initial publication to `https://github.com/guptasakshi06/Graphia`. Initial M00 tip `7cc5a4f` was pushed to `main` and all three codex branches; this checkout stays on `codex/jigisha-app`.
- Remote guidance is included in the single M00 commit and synchronized before this chat ends. No personal sprint, dataset, application or test result changed. All sprint statuses remain TODO; work in this checkout using this handoff.

### One-commit baseline correction — 2026-11-10 12:56 Asia/Kolkata
- User requested replacing the three intermediate setup commits with one root commit named `M00`. Keep this checkout on its existing codex branch and start from that root baseline. Historical hashes above describe pre-squash activity only; current baseline is obtained with `git rev-list --max-parents=0 HEAD`. Setup/evidence files and TODO sprint statuses are preserved.
