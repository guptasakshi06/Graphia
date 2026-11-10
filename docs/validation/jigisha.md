# JB05 — actual application browser validation

Owner: Jigisha Baiswar. Date: 2026-11-10, Asia/Kolkata. JB05 only.
Status: **DONE / READY FOR M02; not merged**. All JB05 acceptance checks passed.

Checkout: `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha`.
Branch: `codex/jigisha-app`. Clean starting tip: `183ff6b` (completed M01).
At start, integration and both personal branches matched this tip. No branch
switch, synchronization mutation, peer change or merge was needed. Production
application/module/configuration/dependency files remain unchanged in JB05.

## What was checked

This is automated browser verification using actual encoded images, the merged
production app and local Tesseract. No OCR response was injected. Source code
inspection and `inspect.getfile` confirmed `app.load_real_provider()` returns
`modules.preprocessing.load_image`, `modules.preprocessing.run_pipeline`, and
`modules.ocr.extract_text` from this checkout. Test providers stay under tests.
This is neither a student review nor a general OCR-accuracy study; SG05 owns
final measurements and M02 freezes combined evidence.

The original four clear fictional images come from `dataset/manifest.json`:

- `income_certificate/income_certificate_clear.png` — Asha Verma, INC-2026-0042.
- `caste_certificate/caste_certificate_clear.png` — Neel Rao, CST-2026-0043.
- `marksheet/marksheet_clear.png` — Mira Sen.
- `identity_proof/identity_proof_clear.png` — Dev Mehta.

Each has the manifest's fictional application ID and ISO issue date. The actual
single/complete/missing downloads are checked against all four expected field
keys, including null certificate numbers for the last two types. These different
fictional people are separate classroom examples, not one verified person's
submission. Readiness does not establish matching identity or official eligibility.

Additional controls live only in `outputs/reports/JB05/inputs/`, outside the
peer-owned dataset. `verify_evidence.py --prepare` creates deterministic Pillow
pages at 1400×1000 using DejaVu Sans 34, with visible SYNTHETIC SAMPLE / no official
validity labels. One Identity Proof has an empty Student Name label; one page
is an unrelated library note. The blank negative control deliberately has no
visible text (identified by filename and this record). The corrupt `.png` is
45 bytes of labeled non-image data. Two identical copies of the income sample
are uploaded from different folders with the same filename
`JB05_FICTIONAL_duplicate.png`. These are actual image/error controls, not known
text substituted for OCR. Do not use them as independent accuracy samples.

## Commands and environment

Run from the checkout above:

```bash
.venv/bin/python -m pip check
MPLCONFIGDIR=/tmp/dip042-matplotlib .venv/bin/python scripts/check_environment.py --json outputs/reports/JB05/environment.json
.venv/bin/python -m unittest discover -s tests -v > /tmp/JB05-tests.txt 2>&1
.venv/bin/python outputs/reports/JB05/verify_evidence.py --prepare
.venv/bin/python -m streamlit run app.py --server.headless=true --server.address=127.0.0.1 --server.port=8505 --server.fileWatcherType=none --browser.gatherUsageStats=false
```

Observed: own Python 3.12.3 environment, all six imports PASS; Streamlit 1.67.0,
Tesseract 5.3.4, eng/osd available. `pip check` PASS. All **101 tests PASS** in
5.858 seconds (`outputs/reports/JB05/tests.txt`). This suite includes separately
labeled fixture/AppTest checks and real OCR module checks; its fixture portions
are not browser evidence. File watching is disabled per M01's established
workaround; restart the server after source edits. No new dependency installed.

## Actual scenarios and downloads

Open `http://127.0.0.1:8505/` in a browser. Keep four checklist types, processed
OCR, median 3, CLAHE, Otsu and no morphology unless specified below. Wait for
uploads to complete, press **Analyze documents**, and wait for the final report.
For every scenario below, JSON is the actual browser download, copied unchanged
from Downloads to `outputs/reports/JB05/<scenario>.json`. Markdown is also an
actual download where listed. DOM snapshots are `<scenario>_dom.txt`.

| Scenario | Exact input/action | Files | Detected / required | Usable | Coverage | Readiness | Status |
|---|---|---:|---|---:|---:|---:|---|
| single | Upload income clear singly | 1 | 1 / 4 | 1 | 25% | 25% | Incomplete |
| complete | Add the other three clear images | 4 | 4 / 4 | 4 | 100% | 100% | Ready |
| missing | Remove clear identity, analyze again | 3 | 3 / 4 | 3 | 75% | 75% | Incomplete |
| unusable | Add missing-name Identity Proof image | 4 | 4 / 4 | 3 | 100% | 75% | Needs Attention |
| edge_batch | Add blank, unknown, corrupt and two same-name copies | 9 | 4 / 4 | 3 | 100% | 75% | Needs Attention |
| checklist_subset | Remove Identity Proof from required checklist | 9 | 3 / 3 | 3 | 100% | 100% | Ready |
| original_source | Choose original OCR, reanalyze same nine images | 9 | 3 / 3 | 3 | 100% | 100% | Ready |
| changed_settings | Same nine / three types / original OCR; choose adaptive threshold | 9 | 3 / 3 | 3 | 100% | 100% | Ready |

JSON and Markdown pairs: `complete`, `edge_batch`, `changed_settings`. The
verifier compares downloaded Markdown byte-for-text with `render_report` of the
corresponding downloaded JSON. It never rewrites the downloaded report files.
All JSON preserves both OCR results, chosen source, settings, raw text, fields,
unique IDs and errors; no image arrays are embedded.

The real OCR missing-name document is **readable=True, usable=False**: its title
is detected, text is long enough, but `student_name` remains null. It appears in
`unusable_types`, not `missing_types`. This tests a missing required field; it
is not a claim that OCR failed to read the entire page. The blank image returns
`no_text`; the unrelated note returns `ok` but type unknown; corrupt data returns
an explicit image-load/OCR error. All nine files stay in the report. The two
identical filenames have the same content-hash portion but different index
prefixes in their IDs; both records survive, with no extra type credit.

Each changed upload/checklist/source/setting invalidates the session report and
its downloads until explicit Analyze. Wait for old readiness heading and download
buttons to disappear, not merely for a widget click to return. A first immediate
checklist observation saw old DOM elements during Streamlit's incremental
rerender; the next settled state cleared them and its recalculated report used
three required types. Final captures explicitly wait for old elements to hide.

## Browser evidence and limitations

Screenshots under `outputs/screenshots/JB05/` are original JPEG browser captures,
not recreated screens. They show the dashboard, real single missing state,
selected fields and both OCR outputs, grayscale, complete readiness, missing
identity, detected-but-unusable identity, nine-file counts, corrupt error and
invalidation states. See the finalized screenshot index and artifact manifest.
Screenshots are viewport crops of a long scrollable app; paired DOM/downloads
provide details outside each viewport. Capture scope is desktop 1280×720.

A browser call timed out during the first final adaptive-settings check. The
initial local server process had stopped (observed `Stopping...`), and the tab
showed Connection error; no changed-settings download was produced then. Cause
was not established. Restarted the same local-only command with detached Python
`subprocess.Popen(start_new_session=True)`, logging to `server-restart.log`,
reloaded, reuploaded the nine controls and restored the same three-type/original/
adaptive choices. Only the completed retry is accepted as changed-settings
report evidence. No source change or workaround in production code was needed.

No production bug, peer-change request or dependency/API change was found.
Synthetic controls and earlier fixture regressions do not establish real-world
accuracy, authenticity, eligibility, matching identity or a universal best DIP
pipeline. No private upload, cloud service, database, ML/API, publication or
student review was involved. M02 remains a separate integration gate; JB06 has
not started.

## Final verification and screenshot index — 15:09 Asia/Kolkata

JB05 **DONE / READY FOR M02, not yet merged**. All eight saved browser scenarios
passed `verify_evidence.py`: exact counts, percentages/statuses, clear-sample types
and all fields, six named stage controls per decodable image, real missing-name/
blank/unknown/corrupt behavior, duplicate record IDs, OCR-source consistency and
adaptive requested/resolved settings. All three downloaded Markdown files exactly
match their paired JSON renderer output. Settled checklist/source/settings DOMs
contain the change notice and no readiness heading or either download button.

```bash
.venv/bin/python outputs/reports/JB05/verify_evidence.py > outputs/reports/JB05/verification.txt
.venv/bin/python -m compileall -q outputs/reports/JB05/verify_evidence.py
git diff --check
```

All PASS. The saved verifier checks evidence, not a fresh browser run. To repeat
the full browser experiment, use the exact scenario actions above; download via
the actual buttons and save files under the scenario names before invoking it.
It creates `artifact_manifest.json` with SHA-256/size for report evidence, inputs,
screenshots and the four original clear images. Its `--prepare` path generates
only labeled negative/duplicate input controls and never fabricates OCR/reports.

All fifteen screenshots were visually inspected. Index (paths relative to
`outputs/screenshots/JB05/`):

| JPEG | Actual state / paired source |
|---|---|
| 01_dashboard.jpg | Empty app, all four required types, instructions and limits |
| 02_single_missing.jpg | single: 1/1/1, 25%/25%, three missing types |
| 03_ocr_fields.jpg | single: Asha Verma/INC fields and both actual Tesseract texts |
| 04_grayscale.jpg | single: expanded fullscreen grayscale of the income sample |
| 05_complete_ready.jpg | complete: 4/4/4, 100%/100%, Ready |
| 06_missing_identity.jpg | missing: 3/3/3, 75%/75%, missing Identity Proof |
| 07_detected_unusable.jpg | unusable: 4/4/3, 100%/75%, Identity Proof unusable |
| 08_edge_batch_counts.jpg | edge_batch: nine retained files, four types, three usable |
| 09_corrupt_retained.jpg | edge_batch: corrupt record, explicit decode error, unknown type |
| 10_checklist_invalidated.jpg | Final settled retry after removing Marksheet from three-type checklist; no report/downloads |
| 11_source_invalidated.jpg | Original OCR selection, change notice, no report/downloads |
| 12_settings_invalidated.jpg | Initial adaptive change, settled notice, no report/downloads; before server interruption |
| 13_adaptive_threshold_view.jpg | changed_settings retry: actual thresholded/morphology images with caption |
| 14_upload_preview.jpg | changed_settings retry: original normalized color image preview |
| 15_readable_report.jpg | changed_settings retry: both download buttons and expanded readable report heading |

`browser_logs.json` retains six connection-error entries from 15:06:10–15:06:18
Asia/Kolkata. Restart log begins at 15:06:19.126; no new warn/error entries were
observed after recovery. Do not report this entire session as error-free. Final
temporary browser tab closed; restarted server was stopped using SIGTERM to the
verified task PID, and `server-restart.log` records `Stopping...`.

No acceptance item remains awaiting a student. No production fixes or peer
requests. Required local commit uses Jigisha's worktree-specific identity;
resolve its immutable hash with `git log -1 --format=fuller -- docs/validation/jigisha.md`.
M02 must inspect the separate live SG05 handoff before merging; this record makes
no claim that SG05 is complete. JB06 waits for M02's frozen evidence.
