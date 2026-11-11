# Shared setup and merge handoff — Sakshi Gupta + Jigisha Baiswar

> A new chat receiving this path, or only the master `HANDOFF.md` path, should execute the next eligible M checkpoint. Complete one checkpoint, update merge/master records, and stop. Do not implement entire personal tracks to make a merge appear ready.

## Current position

- Integration lead: **Sakshi Gupta**. Application/presentation reviewer: **Jigisha Baiswar**.
- Updated: 2026-11-10 16:47 Asia/Kolkata; **M03 DONE**, final technical package verified.
- Active checkpoint: none. Both owner tracks and M00–M03 are complete.
- Final package: [delivery manifest](docs/DELIVERY.md) and [M03 verification](docs/merge/M03.md). Fill in the report cover details before college submission.
- Integration checkout: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi`.
- Final local delivery refs: `codex/integration` and `main`. Resolve the M03 commit with `git log -1 --format=%H -- docs/merge/M03.md`.
- Sakshi branch/checkout: `codex/sakshi-dip`, `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi`.
- Jigisha branch/checkout: `codex/jigisha-app`, `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha`.
- Common baseline: single root commit named `M00` (resolve with `git rev-list --max-parents=0 HEAD`). User requested replacing the three intermediate setup commits with one; history below retains the actual setup evidence. Remote `origin`: `https://github.com/guptasakshi06/Graphia.git`. Cached `origin/main` is M00. Previously published SG01 `6629e0f` remains in the combined history. M03 delivery is local.
- Environment evidence: root, Sakshi and Jigisha PASS; all six imports, `pip check`, Streamlit CLI, Tesseract English and exact 42-distribution snapshot match. See `docs/merge/M00*.json`.
- Latest repository policy: local commits for both owners with one-line sprint explanations; preserve both histories and integrate at the existing gates. No further push until both tracks and verified M03 finish. SG01–SG04/JB01–JB04 are merged at M01; SG05/JB05 are merged and frozen at M02; SG06/JB06 are merged and verified at M03. GitHub publication requires a separate user request.

Read `AGENTS.md`, master `HANDOFF.md`, `PROJECT_BRIEF.md`, `TEAM_CONTRACT.md` and both personal handoffs. The master defines file ownership and academic scope. All commands below are execution instructions for future checkpoints, not claims they have run.

## Merge ledger

| Checkpoint | Depends on | Status | Expected output | Actual commit/evidence |
|---|---|---|---|---|
| M00 | Planning files | DONE | Tested baseline, fixed interfaces, two separate checkouts | `M00` single root commit; `docs/merge/M00.md` + JSON evidence |
| M01 | M00, SG01–SG04, JB01–JB04 | DONE | Real integrated application with first complete upload test | `c1c155d`; `docs/merge/M01.md`; synchronized both tracks |
| M02 | M01, SG05, JB05 | DONE | Frozen tested code and measured evidence for report/slides | 46e4bf9; docs/merge/M02.md + freeze/audit/sync records; synchronized both tracks |
| M03 | M02, SG06, JB06 | DONE | Verified submission package and final master status | [M03 record](docs/merge/M03.md), [delivery manifest](docs/DELIVERY.md), commit containing this record |

## General merge rules

1. Inspect Git history/branches/worktrees/remotes and all dirty changes first. Preserve unrelated work; never use destructive reset, forced checkout, clean, forced push, blanket stash, or an automatic 'ours/theirs' resolution.
2. Use separate checkouts for concurrent people. Never have two chats switch branches in the same directory. Each checkout uses its own `.venv`; system Tesseract can be shared only on the same machine.
3. Latest user Git policy (2026-11-10): automatically create a local commit after each verified SG/JB sprint and M checkpoint, using a one-line explanation. Keep all further commits local until both SG01–SG06 and JB01–JB06 and final M03 are complete and verified. Preserve the already-published SG01 history; do not undo it. Combine both owners' contributions through the existing M01/M02/M03 gates, preserving their authorship; do not merge incomplete tracks early or push intermediate work. Do not invent a GitHub URL or send messages to the other person through tools.
4. Personal handoffs contain live status. Inspect actual personal branches/checkouts and evidence before accepting them as ready. DONE is not proof of a merge; retain separate merged-at records.
5. Both tracks must pause edits during a merge cutoff. Verify clean/recorded states and intended branch tips; do not race a live writer. If an active student edit prevents a stable cutoff, record the concrete obstacle and wait rather than overwriting it.
6. Commit only intended changes after review; use explicit file lists and one-line explanations. Local sprint/checkpoint commits are authorized by the latest user instruction. Preserve correct owner attribution with worktree-specific Git identity settings. Never include `.venv`, private uploads, unrelated files, nested worktrees or secrets.
7. A merge checkpoint can resolve cross-owner integration bugs in the integration checkout, but must log each fix, rerun affected checks and synchronize the fixes back before either personal track continues.
8. Prefer normal local merges preserving both histories. Before merging, record both branch tips; after merging, record the resulting commit, commands, conflict resolutions, checks and unresolved limitations. No merge-success claim until conflicts and verification are resolved.
9. At a completed checkpoint, update master status, delivery tracker, this ledger and the personal merge annotations in the integrated copies. Preserve personal completion/test history. Write `docs/merge/Mxx.md` with the acceptance evidence.
10. Synchronize completed integration changes into each clean feature checkout before the next parallel round. A forward merge of `codex/integration` into each feature branch is sufficient; do not rewrite their history. Reinstall requirements if dependencies changed. Record actual baseline/paths in each personal handoff.
11. If required work or user-only checks are incomplete, record BLOCKED/AWAITING_USER with the exact owner/sprint/action. Do not mark a checkpoint done and do not fabricate student review. Automated verification may be done by the agent; a human walkthrough is recorded only when it occurred.

## M00 — Shared foundation, API freeze and two independent workspaces

**Purpose:** A short common setup so both people can start separate work without duplicate files or incompatible interfaces. This is the only prerequisite for SG01 and JB01; their build tracks then run independently.

### A. Inspect and teach

1. Inspect Ubuntu release, Python version, Git status/history/branch and whether a baseline commit already exists. No application implementation is expected yet, but verify rather than assume.
2. Explain the architecture and ownership: Sakshi handles image → DIP → OCR; Jigisha handles text → type/fields → readiness plus UI. They connect through `TEAM_CONTRACT.md`.
3. Explain branches versus working directories, and why each student has her own handoff/status file. Read the contract and validate that all named functions/keys/options have one owner. Freeze contract v1, or document a necessary small correction now.

### B. Establish reproducible Ubuntu setup

4. Check system tools before installing. Required Ubuntu commands, if missing: `sudo apt update`, then `sudo apt install python3 python3-venv python3-pip tesseract-ocr tesseract-ocr-eng`. Handle unavailable sudo/network truthfully; do not assume success.
5. Create the minimal directories and `modules/__init__.py`; do not generate any functional application module or `app.py` yet. Root is a project checkout, not a nested application folder.
6. Create tested compatible `requirements.txt` for NumPy, `opencv-python-headless`, Matplotlib, Pytesseract, Streamlit and Pillow. Explain that headless OpenCV works with Streamlit/Matplotlib; Tesseract is installed separately. Avoid optional PDF/Pandas dependencies.
7. Use `python3 -m venv .venv`, `source .venv/bin/activate`, `python -m pip install --upgrade pip`, then install requirements. Record direct package versions after actual checks. Automated commands can use `.venv/bin/python` without shell activation.
8. Add `scripts/check_environment.py` and run it for versions/imports/Tesseract path/version/languages. Confirm `eng`; missing engine means M00 is not fully done.
9. Write a starter `README.md` with Ubuntu commands, environment checks, future launch command `.venv/bin/python -m streamlit run app.py`, ownership and separate-checkout instructions. Label launch as planned while `app.py` is absent.
10. Create `.gitignore` before worktrees: ignore `worktrees/`, `.venv/`, caches, temporary files and private uploads. Do not ignore all `outputs/` or all `docs/`, because selected experimental evidence/submission artifacts must be retained.

### C. Establish baseline and isolated branches

11. Create or select `codex/integration` without overwriting an existing branch/worktree. Preserve any initial branch/history. Review and make a local baseline commit containing the planning files, shared dependencies/setup files and appropriate empty-package markers. Do not stage environment-owned hidden directories.
12. Create branches `codex/sakshi-dip` and `codex/jigisha-app` from the same verified baseline, if they do not already exist. If they exist, inspect their contents and reuse safely instead of forcing recreation.
13. Preferred same-machine arrangement: root integration checkout plus separate worktrees at `worktrees/sakshi` and `worktrees/jigisha`. Example command shapes, after confirming branch/path availability:

```bash
git worktree add -b codex/sakshi-dip worktrees/sakshi codex/integration
git worktree add -b codex/jigisha-app worktrees/jigisha codex/integration
```

If branches already exist, omit `-b` and use the existing branch after checking it. Use each directory as the working directory for subsequent commands. Do not copy `.git` or have two concurrent chats share the root.

14. If Git/worktree access is genuinely unavailable, finish unaffected setup, record the exact blocker, and give a concrete alternative using separately located copies plus explicit ownership-based assembly at merges. Do not claim branch merges occurred. Separate files/directories remain mandatory for simultaneous work. On separate machines, clones are an alternative only if a real shared repository/transfer route is available; record it, do not assume one.
15. Create/verify a local `.venv` in each worktree from the same requirements and run the environment check there. For a remote student machine, provide the exact command and wait for verification rather than claiming it was checked from here.
16. Write `docs/merge/M00.md`, update master/merge status and actual paths, commit the shared gate record, then synchronize that foundation update into both clean feature branches. Update personal current-position fields in their own checkouts with actual branch/path/baseline and verified environment information. Keep their sprint statuses TODO.

**Acceptance:** Shared setup imports work; Tesseract English available; contract v1 fixed; baseline recorded; both students have isolated working copies, a known common baseline and their own handoff; no actual app has been generated. If working copies or environment verification are incomplete, state the specific unmet item.

**End of chat:** Provide each student's actual clickable handoff path and say SG01 and JB01 can now proceed independently. Do not run either sprint in this M00 chat.

## M01 — Merge the two code tracks and connect real modules

**Entry:** Sakshi SG01–SG04 DONE and READY; Jigisha JB01–JB04 DONE and READY; actual checkouts/branch tips inspected. If either is incomplete, name the exact missing sprint and personal handoff path; keep M01 waiting.

1. Record intended cutoffs and clean working state. Read peer-change requests, public APIs, test results and both changed-file inventories. Stage/commit intended owner work if needed without including unrelated files.
2. In the integration checkout, merge Sakshi's branch and Jigisha's branch sequentially. Inspect overlap and resolve deliberately. Planning/master files should not have concurrent edits because of ownership rules; preserve both personal histories if any incidental conflict exists.
3. Verify all six module filenames/imports, exact API keys, BGR/RGB handling, field IDs, configuration shape, selected OCR source and readiness formulas. Do not patch a mismatch with silent fabricated defaults.
4. Wire `app.py` to real `load_image`, `run_pipeline`, `extract_text`, classification, extraction and readiness functions. Remove/disable production paths to fake providers. Test-only fixtures may remain under tests; their presence must not affect actual uploads.
5. Run environment/dependency checks, focused module tests, and a real sample through the full pipeline. Suggested commands where files exist:

```bash
.venv/bin/python scripts/check_environment.py
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m compileall -q app.py modules scripts
.venv/bin/python -m streamlit run app.py
```

Tests passing do not replace a real Tesseract run and actual browser upload. Use browser tools if available; otherwise record the exact user UI check needed and keep the affected acceptance item awaiting verification.

6. Verify at least one real upload gives intermediate images, original/processed OCR, conservative type/fields, readiness and downloadable report. Confirm per-file errors do not silently vanish and multiple uploads can be analyzed together.
7. Resolve integration blockers, record changed contracts/dependencies if any, and rerun affected checks. This checkpoint proves integration, not final dataset accuracy.
8. Record a successful M01 integration commit/evidence summary. Update personal merged-at states for their build sprints, master snapshot and merge ledger. Synchronize both personal branches/checkouts from this integrated code and record their next baseline/path.

**Acceptance:** Both tracks' actual code merged; app uses real OCR; a real upload traverses the full flow; focused checks pass or remaining required verification is explicitly awaiting evidence. No stub-based success claim.

**End of chat:** Stop. Sakshi starts SG05 (real dataset/experiments), Jigisha starts JB05 (real browser scenarios/screenshots), in parallel from the M01 baseline.

## M02 — Merge validation fixes and freeze final evidence

**Entry:** SG05 and JB05 DONE/READY from the real M01 baseline. Both provide measured evidence, defect lists and actual commands/results.

1. Inspect stable personal cutoffs, changed files, validation summaries and unresolved cross-owner requests. Merge both branches into integration; preserve measured raw outputs and screenshot provenance.
2. Resolve blocking defects from either validation track in the integration checkout. Keep ownership/change history explicit. If a fix changes pipeline/OCR/rule/readiness behavior, rerun the affected evaluation and UI scenarios before freezing results; old numbers cannot remain marked final.
3. Confirm all approximately eight samples and four quality conditions/types are represented, all seven DIP/OCR comparisons exist, reference text is checked and final raw OCR/CER settings are available.
4. Confirm actual browser checks for full/missing/unusable/duplicate/unknown cases, correct report downloads and state invalidation. Distinguish fixture-only edge cases from actual OCR-driven evidence. A required unverified browser scenario remains awaiting user action.
5. Write `docs/merge/M02.md` with the frozen code baseline and exact final tables/raw-output/screenshot paths plus limitations. No new feature development after this freeze unless a blocking defect requires it; invalidate affected evidence explicitly if changed.
6. Update master delivery state and M ledger; annotate merged SG05/JB05. Synchronize both tracks from the evidence freeze so they produce report/slides against identical results.

**Acceptance:** Required evidence complete/reproducible; blocking defects resolved and affected checks rerun; measurements and screenshots match the same final behavior. Dataset/sample caveats documented.

**End of chat:** Stop. Sakshi runs SG06 (report/DIP viva) and Jigisha runs JB06 (diagrams/PPTX/app viva/demo) independently. Neither edits the other's submission files.

## M03 — Merge submission artifacts and final delivery

**Entry:** SG06 and JB06 READY, including actual report artifact and actual PPTX with render evidence. Diagram insertion into Sakshi's report may be a documented final-assembly task at this checkpoint.

1. Merge both submission branches; preserve source Markdown, editable artifacts, diagram source/images, viva source files and verification records.
2. Insert Jigisha's final architecture/workflow images into Sakshi's report if still pending, then regenerate the final report artifact and re-render/inspect affected pages. Apply the appropriate document/PDF skills at execution time. Do not leave unannounced placeholder diagrams in final delivery.
3. Inspect the actual PPTX/rendered slides; verify diagrams/results/screenshots match M02 frozen evidence. Use the presentation skill/tools for required export/visual verification. An outline is not a completed PPTX.
4. Combine `docs/viva_sakshi.md` and `docs/viva_jigisha.md` into `docs/viva.md`, removing duplicate questions but preserving correct answers. Confirm `docs/demo_script.md` names Sakshi for DIP/OCR and Jigisha for rules/readiness/UI; include shared cross-understanding.
5. Finish `README.md`: Ubuntu setup, environments, Tesseract checks, run commands, architecture/folder structure, sample provenance, selected preprocessing/known weaknesses, checklist/percentages, experiments/reproduction, troubleshooting, limitations, final file paths and short demo steps.
6. Run a final appropriately scoped smoke check on the frozen application and verify output files exist/open. Do not rerun expensive experiments without changes or unresolved concerns. Check that no private uploads or `.venv` directories are included in the delivery.
7. Audit all original deliverables: working source/dependencies/folders, sample dataset, app, screenshots/comparisons/tables, README, report, actual PPTX, architecture/workflow diagrams, viva Q&A and demo. Use both known names correctly; list unresolved administrative placeholders for roll numbers/college/faculty instead of inventing values.
8. Write a final delivery manifest (for example `docs/DELIVERY.md`) with actual file paths, verification evidence and limitations. Update master tracker, M ledger and personal merge annotations. Record the final integration commit and synchronize copies safely if needed.
9. State whether the technical project is complete, what user-only metadata remains and how to run the demo. Do not claim actual college submission or a conducted mock viva. Offer an interactive mock viva as a separate follow-up when requested.

**Acceptance:** Required artifacts physically present and verified; report/slides/diagrams agree with source and evidence; no hidden placeholders for technical results; commands reproducible; both contributions merged. If a required artifact cannot be generated/verified, leave the checkpoint incomplete with the precise remaining task.

## Required update record after every merge session

Update this file and the master at every checkpoint or interruption. When personal work is still active, read its handoff and do not overwrite live personal changes. At a stable merge cutoff, annotate integrated/merged status without erasing source evidence.

```markdown
### Mxx — YYYY-MM-DD HH:MM Asia/Kolkata — session N
- Status before → after:
- Integration checkout / branch / starting commit:
- Sakshi checkout / branch / cutoff commit / ready sprints:
- Jigisha checkout / branch / cutoff commit / ready sprints:
- Merge commands and actual resulting commit(s):
- Dirty/unrelated changes preserved:
- Conflicts, cross-owner fixes and contract/dependency revisions:
- Verification: exact command/scenario, actual result, PASS/FAIL/NOT RUN:
- Evidence/artifact paths:
- Acceptance items still unmet / student-only action:
- Master/delivery/personal merge metadata updated:
- Track synchronization results and actual next baseline:
- Exact next handoff path(s) and eligible sprint(s):
```

## History

2026-11-10: Merge plan written only. No Git baseline, branch, worktree, system/package setup, application implementation or merge has been performed.

### M00 — session 1 — start
- Status: TODO → IN_PROGRESS. Read all seven planning/instruction files.
- Initial checkout: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi`, unborn `master`; no commits/feature branches/remotes. Seven planning files are untracked and will be preserved in the baseline.
- Observed: Ubuntu 24.04.4 LTS, Python 3.12.3, pip 24.0, system Tesseract 5.3.4 with `eng` and `osd`. Project environments/dependencies are not verified yet.
- Next: freeze contract v1; create setup files; install and check root environment; create baseline/worktrees; verify separate environments and synchronize foundation records. No personal sprint is being executed.

### M00 — session 1 — root setup checkpoint
- Root `.venv` created and requirements installed; direct versions pinned after six successful imports and `pip check`. System Tesseract 5.3.4 with English available.
- PASS: environment checker (`docs/merge/M00-environment-integration.json`), Streamlit CLI 1.67.0, compile check. Full commands/versions: `docs/merge/M00.md`.
- Network sandbox DNS prevented the initial pip upgrade; authorized retry succeeded (pip 26.3). No system installation was needed.
- Still IN_PROGRESS: establish baseline/branches/worktrees, verify two independent environments, then synchronize and finalize records.

### M00 — session 1 — workspace checkpoint
- Local setup baseline committed: `09893da4d1fea88d985baa12c0c77221c9750a4e`. Explicit 29-file staging list reviewed; `.venv`, hidden environment metadata, uploads and worktrees excluded.
- Sequential commands succeeded: `git switch -c codex/integration`; `git commit -m "M00: establish local setup and contract v1 baseline"`; `git worktree add -b codex/sakshi-dip worktrees/sakshi codex/integration`; `git worktree add -b codex/jigisha-app worktrees/jigisha codex/integration`.
- Both feature branches start at the same baseline; independent `.venv` creation/install underway. Root remains on integration. The initial master was unborn, with no history to preserve. No remote was added.
- PASS setup-only smoke: NumPy/OpenCV conversions/filter/threshold/CLAHE; Matplotlib PNG rendered/decoded with Pillow; real Tesseract returned `ENVIRONMENT CHECK 042`. Missing-engine and missing-package diagnostics exited 1 as expected. Evidence: `docs/merge/M00-setup-smoke.json`. These are not dataset/application results.

### M00 — 2026-11-10 12:43 Asia/Kolkata — session 1 — verification cutoff
- Status: IN_PROGRESS; setup acceptance checks PASS; foundation record commit/synchronization pending.
- Root/integration and both feature branches originated at `09893da4d1fea88d985baa12c0c77221c9750a4e`. Personal worktrees clean; no concurrent personal writers observed and no personal sprint work exists.
- Both local `.venv` installations completed offline from the wheel cache. Commands and actual results recorded in the personal foundation annotations and `docs/merge/M00.md`.
- PASS: both environment check JSON reports, `pip check`, Streamlit 1.67.0 CLI, distinct venv prefixes, exact 42-distribution snapshot equality. No student-only setup action remains on this machine.
- Master/delivery records and personal setup annotations prepared in the integration snapshot. Next: commit this shared foundation record; forward-merge it into both clean worktrees; verify sync, then mark M00 DONE and stop.

### M00 — 2026-11-10 12:46 Asia/Kolkata — session 1 — completion
- Status before → after: TODO → IN_PROGRESS → DONE. One checkpoint only; no personal sprint executed.
- Integration checkout/branch: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi` / `codex/integration`. Initial state: unborn master, no history/remotes. Initial setup commit `09893da4d1fea88d985baa12c0c77221c9750a4e`.
- Sakshi cutoff: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi` / `codex/sakshi-dip`; Jigisha cutoff: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha` / `codex/jigisha-app`. Both started at the initial commit; no personal work/dirty changes or active writers at the cutoff. All SG/JB sprints remain TODO and unmerged.
- Shared verified foundation commit: `01b3e869f64a7c58f2c4aee31e0cd65cf25c1058` (`M00: record verified isolated environments and workspace handoffs`).
- Actual synchronization commands, sequential in the respective worktrees: `git merge --ff-only codex/integration`. Both PASS, fast-forwarded `09893da` → `01b3e86` with no conflicts.
- Verification after sync: `git rev-parse HEAD` equal in all three checkouts; `git status --porcelain` empty in all three; own handoff, master/merge handoffs, contract, requirements and environment checker byte-identical to integration. Personal annotations are physically present in each owner's checkout.
- Environment PASS in all three: six imports, local venv, Tesseract 5.3.4 with eng/osd, `pip check`, Streamlit CLI, exact 42-distribution snapshot. Root setup-only smoke and expected failure diagnostics PASS. Full commands/results and artifacts: `docs/merge/M00.md` and adjacent JSON/snapshot files.
- Contract v1 frozen without API/schema changes. No dependency requests, conflicts, missing acceptance checks or student-only setup action remain for M00. No human walkthrough, app flow or accuracy claim. Private uploads/environments/worktrees excluded from commits; existing planning text preserved, original brief unchanged.
- Master status/delivery tracker and both personal setup annotations updated. This completion metadata changes documentation only; setup code/dependencies stay at the verified common foundation commit above. Forward-merge the completion record into both clean checkouts, then confirm the final tips/clean states; the final current hash is obtained with `git rev-parse HEAD` rather than a self-referential hash in this file.
- Next independent actions: **SG01**, `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md`; **JB01**, `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha/JIGISHA_HANDOFF.md`.
- Next M gate: M01 still TODO, requires SG01–SG04 and JB01–JB04 DONE/READY in those actual branches. Do not start it in this chat.

### GitHub publication — 2026-11-10 12:52 Asia/Kolkata — start
- User explicitly requested publishing the committed project to `https://github.com/guptasakshi06/Graphia`. This is repository setup only; M00 stays DONE and M01 stays waiting for personal work.
- Current local baseline: `7cc5a4ff424ec8c1e89b2b069b940a58b97430dd`; root and both personal branches inspected before publishing.
- GitHub repository exists and is public. Network-enabled `git ls-remote --symref https://github.com/guptasakshi06/Graphia.git HEAD "refs/heads/*"` returned no refs: empty repository, no remote history to replace.
- Network-enabled Git CLI authentication verified as the repository owner. The connector lacks write permission, so existing local Git history will be published using Git CLI. No token is recorded.
- Next: configure origin, update current remote/setup guidance, commit intended documentation, synchronize clean personal branches, push main plus all three codex branches without force, verify remote hashes.

### GitHub publication — 2026-11-10 12:53 Asia/Kolkata — initial push PASS
- Configured `origin` as `https://github.com/guptasakshi06/Graphia.git` with `git remote add origin https://github.com/guptasakshi06/Graphia.git`.
- Actual command: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push --atomic origin codex/integration:refs/heads/main codex/integration:refs/heads/codex/integration codex/sakshi-dip:refs/heads/codex/sakshi-dip codex/jigisha-app:refs/heads/codex/jigisha-app`.
- PASS: GitHub created all four refs at `7cc5a4ff424ec8c1e89b2b069b940a58b97430dd`. No force, rewritten history, deleted branch or existing remote content. Token handled by GitHub CLI; no credential recorded in project files.
- Branch layout: GitHub `main` is the landing branch; existing worktrees stay on their codex branches. `origin` configuration is shared by linked worktrees. Set upstreams to the matching origin/codex branches.
- Current remote guidance and both personal setup annotations are included in the user-requested single M00 commit; compare remote heads with local heads before reporting final completion. M00 remains DONE, M01 remains TODO; SG01/JB01 remain next and all personal sprint ledgers stay TODO.
- No application/dependency change; prior environment checks remain applicable. `git diff --check`, intended file review, ignored/tracked path checks and final local/remote hash equality are the relevant verification.

### Single M00 commit — 2026-11-10 12:56 Asia/Kolkata — explicit user correction
- User: "not so many commits, just M00" and "remove previous commits and just add 1". This explicitly authorizes replacing the three just-uploaded intermediate commits with one root commit whose message is exactly `M00`.
- Read-only remote inspection confirmed main and all three codex branches still point to `7cc5a4ff424ec8c1e89b2b069b940a58b97430dd`; both personal worktrees are clean. No new remote/student work is being overwritten.
- Preserve the project tree, including the repository documentation, `.gitignore`, handoffs and verified setup. Only Git history and current baseline annotations change. All previous environment evidence remains valid; M00 stays DONE and all personal sprint rows stay TODO.
- Keep a local-only backup ref for recovery. Build one root commit using `git write-tree` and `git commit-tree` without parents; update local refs with expected-old-SHA checks and synchronize the two clean personal working trees. This does not use a destructive reset or change branch names.
- Replace exactly main and the three codex refs using an atomic push with an explicit `--force-with-lease=<ref>:7cc5a4ff424ec8c1e89b2b069b940a58b97430dd` for every ref. Reject any intervening remote change. No blanket force push.
- Before ending: verify one commit named M00, no parent, clean worktrees, matching local/remote hashes and default main. Resolve the final baseline with `git rev-list --max-parents=0 HEAD`; a commit cannot contain its own hash.
- Historical intermediate SHA records above and in M00 evidence describe completed setup steps before the squash; they are not the new baseline.

### Local-commit policy / tracking update — 2026-11-10 13:18 Asia/Kolkata
- Administrative update requested by user; no M checkpoint or personal sprint executed. M00 remains DONE, M01–M03 TODO.
- Root starts clean at `464c884af09bb1d2db686559eaee16cdb9912d59`; Sakshi is clean at published SG01 `6629e0f240023aadb8027032f1e60b6071e34d27`; Jigisha has exactly the five JB01-owned files listed in her handoff, uncommitted at inspection. Preserve every owned implementation/fixture/test file.
- User now authorizes automatic local commits for verified work in both tracks, with one-line descriptions, and no further development pushes until both tracks and M03 finish. Final combined project must include both histories through M01/M02/M03. Earlier SG01 publication is historical and is not undone.
- User confirmed `jigishadebugging` for Jigisha. Read-only public GitHub API confirmed login `jigishadebugging`, ID `146957478`, created 2023-10-04; GitHub's documented ID-based no-reply format gives `146957478+jigishadebugging@users.noreply.github.com`. Local author is Jigisha Baiswar in her worktree only; no GitHub login or global/shared identity replacement is required.
- Verified Jigisha's current JB01 classifier with `.venv/bin/python -m unittest discover -s tests -p test_classification.py -v` and the same command with `-S`: both PASS, 8 methods including 16 fictional cases. These are rule tests, not real OCR.
- Commit the shared policy/tracker files locally and synchronize only into clean, idle personal checkouts. Jigisha's active worktree must wait for a stable cutoff. Preserve separate code tracks; documentation synchronization does not satisfy M01. Resolve actual commit hashes with `git log` in each checkout; record synchronization in the appropriate live handoff.
- Remaining gate: **SG02–SG04**, `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md`; **JB02–JB04**, `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha/JIGISHA_HANDOFF.md`. Next eligible sprints are SG02 and JB02, one per chat. No push in this update.

- Concurrent work discovered at 2026-11-10 13:20 Asia/Kolkata: Jigisha's existing JB01 commit `0b23f1ef8948efa2d2b8d44bea9c8f4009df623c` is correctly attributed to `Jigisha Baiswar <146957478+jigishadebugging@users.noreply.github.com>` (author and committer). Her other chat has started JB02: handoff/fixtures modified and extraction module/tests being added. Do not edit, stage, commit, or merge into that worktree during this active sprint. No duplicate JB01 commit is needed.
- Attempted `git merge --ff-only codex/integration` in Jigisha's worktree exited 128 because her newly created JB01 commit diverged from the policy branch; Git refused before any changes. No merge state, staged edits, or owner file modification resulted. Stop that synchronization until clean/idle; her live handoff already records the local-only/deferred-main preference.
- Effective identity setup verified: only `.git/worktrees/jigisha/config.worktree` overrides name/email after enabling `extensions.worktreeConfig`; Sakshi/root still resolve to Sakshi. This complements the other chat's per-command Jigisha overrides; no credentials or shared/global user identity changed.
- Documentation synchronization is deferred for both personal branches: a subsequent inspection found Sakshi's SG02 is also active and dirty. No policy merge was attempted there. Preserve both active sprints and synchronize only when each has a clean, idle cutoff. No remote push or early main update.

- Final scope/check at 2026-11-10 13:20 Asia/Kolkata: root changes are only `AGENTS.md`, `HANDOFF.md`, `MERGE_HANDOFF.md`; no application files copied/merged. Both live handoffs report second sprints IN_PROGRESS. Do not execute those sprints in this policy chat. Before the next policy synchronization, recheck branch tips, clean status and owner handoffs; then merge `codex/integration` locally with normal history-preserving merges. `main` stays unchanged until verified M03 and both full tracks finish. All new commits remain local.

### M01 — 2026-11-10 13:57 Asia/Kolkata — session 1 — start
- TODO → IN_PROGRESS. Read required project instructions, brief, contract v1, master/merge, M00 foundation evidence and both live personal handoffs/evidence inventories.
- Integration cutoff: codex/integration / f99cafe69af397f02aa978b65dbea10b476a748f, clean.
- Sakshi cutoff: worktrees/sakshi / codex/sakshi-dip / 93a07b1ffe5da4f59941ed65d46e1ad881b115c7, clean, SG01–SG04 DONE/READY; no peer/dependency requests.
- Jigisha cutoff: worktrees/jigisha / codex/jigisha-app / 5bbd086569566c7e7e52fdb18bcd013649123ca3, clean, JB01–JB04 DONE/READY; no peer/dependency requests.
- Both handoffs stop at M01; no active edits observed. Preserve owner histories through sequential normal merges. Local commits only; no push or main update.
- Verify real module contracts, full suite/environment, actual real-OCR sample and browser upload/download. Keep fixture-only tests distinct. SG05/JB05 not executed here.

### M01 — 2026-11-10 14:39 Asia/Kolkata — session 1 — verified code cutoff
- M01 remains IN_PROGRESS only for completion synchronization. Sequential normal merges PASS: Sakshi merge `8951039`, Jigisha merge `a8a0208`; no conflicts or owner-code algorithm fixes. Owner sprint authorship intact. No contract/default/dependency revisions.
- PASS: environment/Tesseract English, pip check; 101 combined tests; final wording-only update 12 UI tests; compile and diff checks. Real four-sample/eight-OCR smoke matches expected fields/types; corrupt fifth file retained, Ready/100%. Repeatable `docs/merge/verify_m01.py` also PASS.
- Actual browser PASS: two existing fictional sample uploads, six stages per file, original/processed OCR ok, fields/type/readability, 2/4 types = 50% coverage/readiness, Incomplete; both report downloads parsed and copied. Final app restarted/reuploaded/analyzed after wording update. Browser warning/error logs were empty at download check. All paths/commands: `docs/merge/M01.md`.
- Runtime issue: recursive Streamlit watching overflowed with nested environments/worktrees; resolved with tested `--server.fileWatcherType=none`, documented in README. Restart after code edits. No system-watch setting changed.
- Browser origin access was declined during an optional later screenshot-framing adjustment. Stopped all browser actions; did not circumvent it. Earlier downloaded reports, complete final DOM and saved partial-viewport screenshot remain valid. This is not a failed OCR/browser acceptance check or automatic shell-approval rejection.
- Root handoffs/master/README updated; source worktrees rechecked clean and still at recorded tips. Commit this verified baseline, then forward-merge it sequentially into both tracks. No SG05/JB05 or later M gate started; no push/main update.

### M01 — 2026-11-10 14:40 Asia/Kolkata — session 1 — completion
- Status before → after: TODO → IN_PROGRESS → DONE. One merge checkpoint only; all M01 acceptance checks complete; no required student-only action or unresolved integration defect.
- Integration start `f99cafe`; Sakshi source `93a07b1` (SG01–SG04 READY); Jigisha source `5bbd086` (JB01–JB04 READY). All clean/stable at cutoff; no unrelated edits. Actual source merge commits `8951039` and `a8a0208`, no conflicts, histories/authors preserved.
- Verified code/evidence commit `c1c155d5ab9368f13ede5781470ff4cc0673d38a` (`M01: verify integrated real OCR application and record baseline`), author/committer Sakshi Gupta with root worktree-specific identity. No shared/global identity change. An extra EOF blank in the Markdown smoke export was caught by staged diff check, corrected in exporter/artifact, and rechecked before commit; no algorithm/test result changed.
- Executed sequentially: `git -C worktrees/sakshi merge --ff-only codex/integration --quiet`, then the same in `worktrees/jigisha`: PASS, both feature tips equal `c1c155d5ab9368f13ede5781470ff4cc0673d38a`, all three checkouts clean afterward. Original owner histories remain ancestors; branch names/independent .venv unchanged.
- Post-sync own-environment checks in BOTH tracks: imports `app.load_real_provider()` with all three real functions, validates empty-input configured readiness as Incomplete, reports own sys.prefix, `pip check`: PASS; both worktrees clean, owner author identities preserved (Sakshi / Jigisha respectively).
- Earlier full verification/evidence: 101 combined tests PASS, 12 final UI tests PASS, environment/Tesseract/compile/diff PASS, real production and browser smoke/downloads PASS. Exact commands/results/limitations/artifacts in `docs/merge/M01.md`. Runtime watcher workaround documented; browser optional reframing refusal respected. Local server stopped cleanly, exit 0.
- Master/delivery tracker and both integrated personal handoffs now annotate build sprints merged at M01, validation sprints TODO and eligible. Completion metadata changes only documentation; forward-merge its containing commit into both clean tracks, then verify identical tips/clean states. Resolve final containing hash with `git log -1 --format=%H`, avoiding a self-reference.
- No SG05/JB05, M02/M03, human walkthrough, final experiment freeze, report/slides, push or main update. Local origin/main remains M00 `464c884af09bb1d2db686559eaee16cdb9912d59`; no remote operation performed.
- Exact next Sakshi action: `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md and execute SG05 only. Verify the work and update the handoff before stopping.`
- Exact next Jigisha action: `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha/JIGISHA_HANDOFF.md and execute JB05 only. Verify the work and update the handoff before stopping.`
- Next merge requires both SG05 and JB05 from these synchronized checkouts; use `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/MERGE_HANDOFF.md` for M02. Stop after final metadata synchronization.

### M02 — 2026-11-10 15:59 Asia/Kolkata — session 1 — start
- TODO → IN_PROGRESS. Read project instructions, master, original brief, contract v1, M00/M01 foundation evidence, both live personal handoffs and validation summaries.
- Integration root / codex/integration starts clean at `183ff6bfa6e67e2156eafc282044eb151e07ad39`.
- Sakshi: worktrees/sakshi / codex/sakshi-dip / `c98d89370960faeb2fb626ae270669769627fb4c`, clean, SG05 DONE/READY, SG06 TODO; correct Sakshi author/committer.
- Jigisha: worktrees/jigisha / codex/jigisha-app / `80a38e4eb4cf0de179d581a1ab1e38f073fbc22f`, clean, JB05 DONE/READY, JB06 TODO; correct Jigisha author/committer.
- Both validation commits descend from synchronized M01 `183ff6b`; changed-file inventories are owner evidence/runner/tests/handoffs only. Production app/modules/config/dataset/contract/dependencies unchanged in both; no unresolved peer requests or required student action in either track. No active edits observed.
- Merge sequentially preserving both authors; audit source/data/evidence hashes, all seven comparisons, browser downloads/scenarios/state invalidation and full regression/environment. Freeze only after actual checks. Preserve raw outputs/screenshots, no new features/defaults, no SG06/JB06/M03/main update/push.

### M02 — 2026-11-10 16:02 Asia/Kolkata — session 1 — verification checkpoint
- M02 IN_PROGRESS for completion synchronization only. Sakshi c98d893 and Jigisha 80a38e4 merged sequentially with normal merge commits c335709 / bc35ef9, no conflicts. No owner behavior/API/default/dependency fixes required; production remains M01 183ff6b.
- PASS: 107 tests in 8.409s; environment/imports/Tesseract eng+osd/pip; compile/diff; 387-file frozen inventory; matching references/source hashes; all seven comparisons/112 method rows; stored 282/282 independent repeat hashes; eight actual browser download scenarios, three exact Markdown pairs and three settled invalidation DOMs; all 15 screenshot hashes/decodes. No fresh browser/whole experiment rerun or human review claimed.
- Final results/paths/limitations and snapshot caveats in docs/merge/M02.md. Original/default CER0 is a tie; related synthetic samples do not prove general accuracy. Historical SG05/JB05 candidate wording preserved in raw evidence and superseded by the merge freeze. No invalidated evidence or required student action.
- Master delivery tracker and integrated personal annotations updated; local verified-freeze commit and sequential forward synchronization next. No SG06/JB06/M03/main update/push. Source worktrees must be rechecked clean/stable before each synchronization.
- A documentation helper initially rejected an outdated SG05 ledger string before writing personal records; corrected against the actual row, with no source/evidence change or effect on passing checks.

### M02 — 2026-11-10 16:04 Asia/Kolkata — session 1 — completion
- Status before → after: TODO → IN_PROGRESS → DONE. One M checkpoint only; all acceptance checks complete, no required student-only action or unresolved blocking defect.
- Root / codex/integration started at 183ff6b; clean owner cutoffs c98d893 (SG05) and 80a38e4 (JB05) merged as c335709 / bc35ef9. No conflicts or behavior/default/contract/dependency changes; both owner authorship histories remain intact.
- Verified freeze commit `46e4bf936518a747a3ce5fe7796ba2c9deede991` (`M02: verify and freeze combined OCR and browser evidence`), author/committer Sakshi Gupta using root worktree-specific identity. All 11 intended record/verifier files reviewed; staged diff check PASS.
- Actual sequential synchronization: `git -C worktrees/sakshi merge --ff-only codex/integration --quiet`, then same for worktrees/jigisha: PASS. All three HEADs equal 46e4bf9, clean afterward; handoffs/freeze physically byte-identical. Both independent .venv evidence audits, real-provider imports and pip checks PASS, correct worktree-specific owner identities retained. Evidence: docs/merge/M02-sync.json.
- Verification: 107 tests in 8.409s, environment/eng/pip/compile/diff PASS; 387 frozen hashes, all four types/quality conditions, seven comparisons, original/default exact synthetic results and adverse alternatives, 282-file independent repeat record, all eight actual browser scenarios/three Markdown pairs/invalidation DOMs/15 screenshots PASS. Exact commands, artifacts, provenance caveats and limits: docs/merge/M02.md. No fresh M02 browser experiment or human review asserted.
- Master delivery tracker and integrated/live personal merge annotations updated; SG05/JB05 DONE and merged at M02. SG06 and JB06 remain TODO and are now eligible using this same frozen evidence. M03 remains TODO until both actual submission artifacts/render checks are ready.
- Completion metadata follows the verified freeze locally; forward-merge its containing commit into both still-clean checkouts and verify final equal tips/clean states before stopping. Resolve final containing hash with `git log -1 --format=%H`; no self-referential commit hash is invented.
- No SG06/JB06/M03, push, fetch, publication, main update, report/slides generation, student walkthrough or mock viva. Cached origin/main remains M00 464c884; local main does not exist. No remote operation performed; published SG01 history preserved.
- Exact next Sakshi action: `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi/SAKSHI_HANDOFF.md and execute SG06 only. Verify the work and update the handoff before stopping.`
- Exact next Jigisha action: `Read /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha/JIGISHA_HANDOFF.md and execute JB06 only. Verify the work and update the handoff before stopping.`
- Next merge: M03 at /home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/MERGE_HANDOFF.md after both submission sprints are verified. Stop after final metadata synchronization.

### M03 — 2026-11-10 16:43 Asia/Kolkata — session 1 — start
- TODO → IN_PROGRESS. Clean integration cutoff `bf3d34e` and both clean, idle owner checkouts verified before editing this ledger.
- Sakshi `codex/sakshi-dip` at `784544fee91755c79b3f42d4af9d21618b0289e7` (SG06 DONE); Jigisha `codex/jigisha-app` at `6ad9d573c554c1fb8ac95049726963af5d1dd7d4` (JB06 DONE). Each is the single owner-authored commit after the common M02 tip; both completion handoffs and actual report/deck artifacts are committed. JB06 deck SHA-256 matches its recorded verification. All twelve sprint commits exist with the correct owners.
- Merge the recorded commits, insert both diagrams, rerender, audit frozen evidence and perform a real application smoke test before finalizing.

### M03 — 2026-11-10 16:45 Asia/Kolkata — session 1 — verification checkpoint
- Both normal merges passed without conflicts: Sakshi `d39c7c8`, Jigisha `80e9e6a`. Production files and frozen inputs are unchanged from M02.
- PASS: 107 tests, environment and pip checks, compile check, fresh eight-call Tesseract smoke, Streamlit health, 387 frozen hashes and saved scenario audit.
- PASS: inspected all 10 report pages and all 12 slides. Both final diagrams and six frozen images match the report embeds, and the deck content and frozen media checks passed. The PDF is the inspected DOCX export. Final package inventory and status updates follow.

### M03 — 2026-11-10 16:47 Asia/Kolkata — session 1 — completion
- TODO → IN_PROGRESS → DONE. Integration started at `bf3d34e`. Both idle source cutoffs were clean: SG06 `784544f`, JB06 `6ad9d57`. Merges `d39c7c8` and `80e9e6a` preserve both owners’ histories. No conflicts or unrelated edits.
- Both JB06 diagrams are embedded in the rebuilt report. The PowerPoint is the verified JB06 artifact. The final viva contains 25 questions and the demo includes both roles. The master, delivery tracker and integrated personal handoffs record the merged status.
- PASS: 107 tests, real eight-call OCR smoke, local Streamlit health, 387 frozen hashes and the saved M02 browser scenarios, ten report pages, twelve slides, and all 14 brief deliverables. Exact commands, scope and file hashes are in `docs/merge/M03.md`. M03 reused the frozen browser evidence.
- After package verification, commit the M03 delivery with Sakshi's worktree identity. Sequentially run `git -C worktrees/sakshi merge --ff-only codex/integration` and `git -C worktrees/jigisha merge --ff-only codex/integration` after rechecking both cutoffs. Create local `main` at the same verified commit and confirm all four refs agree and the three checkouts are clean. The final commit is located by `git log -1 --format=%H -- docs/merge/M03.md`. Publication is separate.
- No later sprint or checkpoint is pending. Before college submission, fill in both roll numbers, college, department and faculty guide in `docs/project_report.docx`, apply any prescribed cover format and export the updated PDF. Run the local demo from `docs/demo_script.md`. No college submission, student walkthrough or mock viva was recorded.

### Post-M03 follow-up — 2026-11-10 20:45 Asia/Kolkata — bilingual OBC photo
- Verified a user-supplied 768 × 1024 photo in memory. The previous English original OCR read the OBC heading and certification sentence but returned Unknown Document. The default thresholded path lost key text. The holder is described in a sentence and the certificate number is labeled in Hindi.
- Local integration update on `codex/integration` from `756fc3b`: match the full OBC heading, extract the holder bounded by the certification wording and the relationship phrase, and require the Hindi certificate label on the number line. The parser ignores the application number and withholds conflicting values. English + Hindi selects Tesseract PSM 4 and reports missing language data explicitly.
- PASS: 110 tests via `.venv/bin/python -m unittest discover -s tests`. A prior run found that the SG05 test compared historical source hashes to the live checkout. It now hashes the recorded M02 Git revision. The original M02 verifier separately passed all 387 hashes in the clean Sakshi worktree at `756fc3b`.
- PASS: four fictional demo inputs through the unchanged default English settings, eight real OCR calls and all expected fields. Real photo passed through the Streamlit entry point with both report controls and a Ready result for the caste-only demo checklist. Independent English OCR agreed on the name and OCR of the printed number row agreed with bilingual full-page OCR. No private photo, OCR transcript or identifier is tracked.
- Preview started locally at port 8506 using `TESSDATA_PREFIX="$PWD/.codex/ocr-tessdata-ubuntu" .venv/bin/python -m streamlit run app.py --server.headless=true --server.address=127.0.0.1 --server.port=8506 --server.fileWatcherType=none --browser.gatherUsageStats=false`. The ignored model directory uses Ubuntu's Hindi OCR data with the existing English model. Health and browser landing view passed. Select **English + Hindi**, **original** OCR and **Caste Certificate** as the only type when checking this file by itself.
- Scope: the observed bilingual OBC layout. The earlier 387 × 516 photo still needs a clearer original for OCR. The published M03 package remains available on `main` at `de60bcd`. Locate this local update with `git log -1 --format=%H -- modules/classification.py`.

### Post-M03 follow-up — 2026-11-10 21:01 Asia/Kolkata — income and PAN layouts
- On `codex/integration` from `983f2cd`, added income detection for the Hindi title and issuer-prefixed variant, recognized explicitly labeled applicants and bounded English certification sentences, and distinguished the Hindi certificate number from the application number. The exact Hindi certificate label, colon and a single numeric value can recover a short damaged number-marker token.
- PAN card headings map to Identity Proof for this demonstration checklist. The rule reads the holder from an explicit Name label on the same or next nonempty line and leaves conflicting or ambiguous values missing. It does not extract the PAN number or use the parent's name.
- References: the Uttar Pradesh public service [income certificate title](https://upcmo.up.nic.in/janhit.htm), Railway Recruitment Board [blank income certificate form](https://www.rrbranchi.gov.in/upload/files/pdf/01_04_15pm8960e89d3646ba4378520de1773481cf.pdf) and Protean [PAN card specimen and field names](https://www.protean-tinpan.com/downloads/TIN-website-popup-reg.QRcode.pdf). No government or user documents were copied into the project.
- PASS: 112 tests via `.venv/bin/python -m unittest discover -s tests`. The first real bilingual OCR smoke on a fictional image revealed the number marker was misread. After the guarded correction, standalone PAN passed English OCR, and a two-image fictional batch passed the real English + Hindi OCR path in Streamlit AppTest. Both types and all required fields matched, with two download controls and Ready for the matching two-type checklist.
- Latest local preview is port 8507 with the existing ignored Hindi data directory. Browser landing and health passed. For a mixed batch select **English + Hindi** and **original**. The user's exact income certificate and PAN layouts are pending a local trial. Public `main` remains at `de60bcd`. Locate the local follow-up with `git log -1 --format=%H -- modules/classification.py`.

### Post-M03 follow-up — 2026-11-11 Asia/Kolkata — camera photo OCR
- Baseline `b3b4195`, local `codex/integration`. The supplied PAN photo was sideways and both standard bilingual OCR paths returned no text. The supplied UP income photo had a large background and the standard paths returned text without a recognized title.
- Added **Auto photo**, which compares the existing OCR results and can crop a bright paper area, resize it in grayscale, and try quarter turns. The observed UP printed income form has a guarded regional reader. It requires the issuer heading and checks the application row separately. Two OCR passes must agree on the 12-digit certificate number and on the holder's name. Unresolved values remain missing. The photo method is recorded with each report.
- Added title coverage for e-PAN, Hindi caste certificates and marks statement variants, and explicit holder labels for marks statements. Layout references include the [Income Tax Department PAN specimens](https://www.incometaxindia.gov.in/documents/20117/43154/18__PAN__English.pdf/0f590273-a856-dee2-9053-76f8c0aa4127?t=1762672726879&version=1.0) and [CBSE marks statement circular](https://www.cbse.gov.in/cbsenew/documents/SUBMISSION_EXAMINATION_FORMS_PRIVATE_CLASS_X_2526_08092025.pdf). These references informed rules. No training run or general accuracy measurement was performed.
- PASS: `OMP_THREAD_LIMIT=1 .venv/bin/python -m unittest discover -s tests`, 114 tests. This includes a rotated fictional input using real Tesseract. The exact two supplied photos also passed real OCR through the Streamlit entry point. Both document types, both holder names and the income certificate number matched the printed values. The matching two-type demonstration checklist returned Ready and both export controls appeared. Full-page text in the income photo can still contain OCR errors. No private inputs, OCR text or identifiers are tracked.
- Latest local preview `http://127.0.0.1:8508/` uses the ignored Hindi OCR data folder. The visible browser tab has **English + Hindi**, **Auto photo**, **Income Certificate** and **Identity Proof** selected. Use this preview for the two-photo retest. Published M03 is on `main` at `de60bcd`. Locate the local follow-up with `git log -1 --format=%H -- modules/photo_ocr.py`.

### Post-M03 follow-up — 2026-11-11 Asia/Kolkata — restore the local app
- Port 8508 had no listener and the health request was refused. The integration checkout at `ede9548` was clean and its Python environment and local Hindi OCR data were present.
- Installed and enabled the Ubuntu user service at `/home/ubuntu/.config/systemd/user/graphia.service`. It starts Graphia at login, restarts after a process failure, and serves the existing loopback URL `http://127.0.0.1:8508/`. The service sets the existing local Hindi model directory and uses the integration checkout's virtual environment.
- PASS: `systemctl --user is-active graphia.service`, `systemctl --user is-enabled graphia.service` and a healthy response from `/_stcore/health`. Retested the two supplied photos through the live browser upload and Analyze controls using English + Hindi and Auto photo. The app detected Income Certificate and Identity Proof, showed Ready for those two required types, and displayed both report download controls. Private images and OCR text are absent from this record.
- If the local service is ever stopped, run `systemctl --user start graphia.service` and open `http://127.0.0.1:8508/`. Use `systemctl --user status graphia.service` to inspect startup.

### Post-M03 follow-up — 2026-11-11 Asia/Kolkata — Streamlit workspace redesign
- On `codex/integration` from `b6af377`, put upload and analysis together, kept the checklist and OCR choices alongside them, and moved image processing controls behind an expander. The results show readiness and download actions first, then a file picker with separate tabs for fields, OCR text, and image stages. OCR, readiness rules, defaults, and report formats are unchanged.
- PASS: `OMP_THREAD_LIMIT=1 .venv/bin/python -m unittest discover -s tests` (114 tests), Python compile and Git diff checks. A browser run with all four fictional demo images returned Ready with all four required types usable. The marksheet and caste certificate fields matched their references, the OCR and image tabs worked, and both report downloads completed. No private documents were used for this check.
- Restarted `graphia.service`, verified `/_stcore/health` and the browser workflow on `http://127.0.0.1:8508/`, and stopped the temporary port 8510 preview. Reload the local app to use this version. The UI checkpoint is local; no GitHub push was performed.

### Post-M03 follow-up — 2026-11-11 23:30 Asia/Kolkata — browser connection recheck
- An existing in-app tab for port 8508 showed a connection-refused page. `graphia.service` was active and enabled, and `/_stcore/health` returned HTTP 200. The service had been running since the UI restart; no further restart or app code change was needed.
- Opened a fresh tab at `http://127.0.0.1:8508/` and ran Upload → Analyze with four fictional demo images. Graphia returned Ready with all four required types usable. Reloaded the fresh tab and left it open at the upload screen. If the older tab still shows the connection error, use the fresh tab or reload the older one.

### Post-M03 follow-up — 2026-11-11 23:37 Asia/Kolkata — phone photo settings and DIP review
- Started on `codex/integration` at `7022680`. Service health returned HTTP 200. Reproduced the reported behavior locally with the previously supplied photos: default English / Processed OCR returned two Unknown Documents, while English + Hindi / Auto photo recognized both with all required fields. Both runs produced all six DIP stages for each photo.
- Added **Use phone photo settings** to select the working OCR options together, a **View results** link after analysis, and a side by side original and selected DIP stage comparison. Pipeline operations, controls, OCR defaults and report formats are unchanged.
- PASS: `OMP_THREAD_LIMIT=1 .venv/bin/python -m unittest discover -s tests` (114 tests) and `git diff --check`. Through Streamlit AppTest with real OCR and the local Hindi model, the preset made both previously supplied photos usable for their two-type checklist, produced six stages per photo and showed both export controls. No private inputs or values were saved to the project. In the browser, a fictional marksheet verified upload, the results link and the stage selector with all six stages and two visible comparison images.
- Restarted `graphia.service`, checked HTTP health on port 8508, verified the preset in the live browser and left a tab open with it applied. Stopped the temporary port 8510 preview. For a two-photo retry, select Income Certificate and Identity Proof as the required types, upload the photos, and press Analyze documents. No GitHub push.

### Post-M03 follow-up — 2026-11-12 Asia/Kolkata — document-specific extraction
- On `codex/integration` from `1e3ed01`, added PAN number, income amounts and caste category to the extracted fields table and both report formats. Grade sheets now recognize the holder's Name label. Auto photo can read tighter headers for the supplied layouts. The UP amount fallback uses two agreeing reads of the amounts in words when the numeric OCR is unreliable. The DIP pipeline, all six stage views and the checklist criteria remain available.
- PASS: `OMP_THREAD_LIMIT=1 .venv/bin/python -m unittest discover -s tests` (115 tests), `git diff --check`, and a Streamlit AppTest using real Tesseract on five local photos (PAN, income, marksheet, SC and OBC). All requested values were present and both income periods were checked against the printed wording. Six stages were present for each image, and report details were retained. The smaller certificate can still lack the holder name or certificate number used by readiness. No private inputs or extracted values were added to Git.
- Restarted `graphia.service`, checked HTTP health on port 8508 and left the upload screen open with English + Hindi and Auto photo selected. Upload and analyze, then open Extracted fields for the file. No GitHub push.

### Post-M03 follow-up — 2026-11-12 Asia/Kolkata — additional OCR samples
- Started at `abc2c6a` on `codex/integration` to compare the requested values against ten new fictional JPEG samples with alternative headings, lighting, perspective, and orientation. Used English + Hindi and Auto photo through Streamlit AppTest with real Tesseract.
- Compared the reported fields to the printed fixture values. Matches: PAN 1/2, annual income 2/2, marksheet holder 2/2, SC 2/2, and OBC 2/2. The one miss was the angled sample whose heading said only `Permanent Account Number` without `Card`; Graphia returned Unknown Document and no PAN value. The rotated e-PAN sample was correctly read. All ten results contained six DIP stages and the two report controls appeared.
- Generated the JPEGs in a temporary directory with Pillow and OpenCV. This was a controlled test of new layouts and simulated photo conditions. App code and local service were unchanged. A future PAN change should test a heading without `Card` while guarding against unrelated tax forms.

### Post-M03 follow-up — 2026-11-12 Asia/Kolkata — short PAN heading
- Started at `f5d8c41` on `codex/integration`. Recreated the angled fictional PAN JPEG from the previous run using the same rendering and noise seed for a before and after comparison.
- The shorter heading now works when an issuer cue is present and the next nonblank line is a PAN-shaped number. Classification, PAN number extraction, and holder name extraction use the same heading check. Tests cover an inline tax-form field, missing corroboration, and conflicting numbers.
- Before the fix the recreated image returned Unknown Document with no number. After the fix, Streamlit AppTest and browser upload on port 8508 both returned Identity Proof and displayed the exact fictional number printed in the image. The browser used English + Hindi and Auto photo. `OMP_THREAD_LIMIT=1 .venv/bin/python -m unittest discover -s tests` passed all 116 tests. Restarted `graphia.service` and verified HTTP health. The fix is local.

### Post-M03 follow-up — 2026-11-12 Asia/Kolkata — checklist field alignment
- Started at `dad3fef` on `codex/integration`. The active checklist still used the original demo field requirements for the certificates and identity proof. Align the app checklist with the fields requested for the phone photos and verify with the actual documents.
- The app now reads `config/document_checklist.json` and requires a PAN number, an income amount (annual, monthly, or total), the marksheet holder's name, and a caste category. Readiness uses optional document details as well as the original field mapping. The frozen demo configuration stays at `config/requirements.json`.
- PASS: `OMP_THREAD_LIMIT=1 .venv/bin/python -m unittest discover -s tests` (117 tests) and `git diff --check`. Streamlit AppTest with real Tesseract and the five supplied photos returned Ready with 4/4 required types using either SC or OBC. The old checklist on the same OCR records returned Needs Attention for missing holder names and certificate numbers on the income and SC photos. A PAN-only checklist returned Ready. All six DIP stages per image and both report buttons were available.
- Restarted `graphia.service`, checked HTTP health and verified the new requirements in the browser at port 8508. Left the upload screen open with English + Hindi and Auto photo selected. The user can re-upload the full set, or select only the type under test in Required document types. No private photos or values were stored in Git.

### Post-M03 follow-up — 2026-11-12 Asia/Kolkata — default photo OCR and DIP review
- Started from `d76adf2` on `codex/integration`. Investigating default OCR settings, selection against the active checklist, and the display of resolved DIP parameters.
- Auto photo now starts by default and uses English + Hindi when the local Tesseract model is available. Candidate selection checks the active document field requirements before ending recovery. Original and Processed OCR remain selectable.
- Image stages opens at Thresholded and compares it with the original. Threshold captions show the measured Otsu cutoff or the configured global/adaptive settings. Enhanced describes the selected contrast method and shows the CLAHE clip limit when used.
- PASS: `OMP_THREAD_LIMIT=1 .venv/bin/python -m unittest discover -s tests` (118 tests) and `git diff --check`. Real Tesseract through Streamlit AppTest read the printed PAN number from a sideways fictional JPEG using default bilingual Auto photo. The matching checklist returned Ready. Verified six stages and both Otsu and CLAHE captions. No failing upload accompanied this request, so this run used a fictional photo.
- Restarted `graphia.service` and verified HTTP health at `http://127.0.0.1:8508/`. Next action: reload that URL, upload the photo, and select Analyze documents. Local integration checkpoint only.

### Publication — 2026-11-12 Asia/Kolkata — final app
- User requested publishing the final app to `guptasakshi06/Graphia` using `jigishadebugging`. Merged verified integration commit `3322a2b` with GitHub main at `3581d57` in a temporary checkout. Both histories and original authors are preserved. The app, modules, config, and tests match the integration checkout.
- PASS: 118 tests via `OMP_THREAD_LIMIT=1 .venv/bin/python -m unittest discover -s tests` using the integration virtual environment from the release checkout. The staged diff passed `git diff --cached --check`. The four untracked IEEE drafts are outside the app release.

### Streamlit Community Cloud preparation — 2026-11-12 Asia/Kolkata
- Prepared the published `main` from `a3c5300` in a temporary checkout. Added `packages.txt` for Tesseract, English and Hindi. Updated the upload caption to describe processing on the app server.
- PASS: Python 3.12 dependency resolution with `python -m pip install --dry-run --ignore-installed -r requirements.txt`, 118 local tests, and staged diff check.
- Deploy `guptasakshi06/Graphia`, branch `main`, entry point `app.py`, with Python 3.12. The Community Cloud workspace is at its sign-in page. After signing in and deploying, verify the public app with a fictional sample.
