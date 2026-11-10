# Project 042 Document Intelligence for Application Readiness

Students: **Sakshi Gupta** and **Jigisha Baiswar**.

This local Python project demonstrates image preprocessing, Tesseract OCR,
rule-based document classification, field extraction and a configurable
demonstration scholarship checklist. Readiness describes the configured
presence and usable information only. It does not establish authenticity,
official eligibility or whether documents belong to the same person.

The technical package is complete at M03. The [delivery manifest](docs/DELIVERY.md)
lists the submission files, verification and cover details still needed.

## Ubuntu setup

Run these commands from a checkout of the verified M03 package. In the original
workspace, the integration directory already contains the application.

Check the tools first:

```bash
python3 --version
git --version
tesseract --version
tesseract --list-langs
```

Only if required tools are missing, install them on Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git tesseract-ocr tesseract-ocr-eng
```

Run the following from the checkout you intend to use:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/check_environment.py
python -m pip check
```

The environment checker prints JSON and exits with zero only when all six
dependencies import, a virtual environment is active, and Tesseract runs with
`eng` language data. `--json path/to/report.json` also saves its observations.
Use `.venv/bin/python` instead of activation when running automated commands.
To reproduce the complete M00 dependency snapshot, install with
`python -m pip install -r requirements.txt -c docs/merge/M00-requirements-lock.txt`.

NumPy represents pixel arrays; OpenCV performs DIP operations; Matplotlib shows
comparisons; Pillow reads/creates images; Pytesseract calls the separate system
Tesseract engine; Streamlit provides the UI. `opencv-python-headless` avoids
desktop GUI dependencies and works with Streamlit/Matplotlib. Do not install a
second OpenCV wheel alongside it. No optional PDF or direct Pandas dependency is
needed; Streamlit may install Pandas as one of its own dependencies.

## Separate workspaces

| Work | Branch | Checkout |
|---|---|---|
| Integration | `codex/integration` | `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi` |
| Sakshi's DIP/OCR | `codex/sakshi-dip` | `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/sakshi` |
| Jigisha's rules/UI | `codex/jigisha-app` | `/home/ubuntu/Documents/ChatGPT/DIP_Jigi_Sakshi/worktrees/jigisha` |

A branch records a history of commits. A worktree is a separate folder checked
out on a branch. These worktrees share Git's history but have independent files
and independent `.venv` folders. Never switch two chats' branches in one folder.
Do not copy or move a `.venv`; recreate it from requirements in its checkout.

The [merge handoff](MERGE_HANDOFF.md) records the final integration. The personal
handoffs in each checkout record its sprint history. The [team contract](TEAM_CONTRACT.md)
documents the module interfaces, processing options and report fields.

## Folder layout and local launch

```text
modules/             Plain Python DIP, OCR, classification, extraction and readiness
scripts/             Environment check, dataset generator and experiment scripts
config/              Fictional demonstration requirements JSON
dataset/             Eight labeled fictional samples, references and provenance
tests/fixtures/      Labeled development fixtures (not OCR evidence)
outputs/             Selected experiment, screenshot and report evidence
docs/merge/          Executed merge-checkpoint evidence and setup versions
docs/sprint_notes/   Owner teaching and verification records
worktrees/           Ignored independent personal checkouts
.venv/               Ignored checkout-local Python environment
```

Run from the chosen checkout (each has its own environment):

```bash
.venv/bin/python -m streamlit run app.py --server.address=127.0.0.1 --server.fileWatcherType=none --browser.gatherUsageStats=false
```

Open the printed local URL, upload fictional images from `dataset/`, keep the
demonstration checklist/default settings and press **Analyze documents**. Review
six image stages, original/processed OCR, type, fields and readiness; download
JSON or Markdown. Changing inputs clears results until Analyze is pressed again.
The default is median 3 → CLAHE 2.0/8×8 → Otsu → no morphology, English PSM 6.
A type is usable when one candidate has sufficient OCR text and its configured
fields. Coverage counts detected required types; readiness counts usable types,
each divided by the number of required types. Duplicates count once.

## Architecture and sample evidence

Streamlit decodes each upload, runs the original and processed images through
Tesseract, then uses the selected OCR text for title matching and field extraction.
The readiness module checks those records against the selected JSON checklist.
The [architecture diagram](docs/diagrams/architecture.png) shows the modules and
the [workflow diagram](docs/diagrams/workflow.png) shows the three possible outcomes.

The [dataset](dataset/README.md) contains eight labeled fictional images from four
generated layouts. Four are clear and four are related low-contrast, noisy or
slightly blurred derivatives. Original and default OCR tied at zero pooled
character error rate on this set. Some alternatives damaged text. For example,
global threshold 127 blanked the faint Income Certificate. If processing damages
text, select original OCR and analyze again. The experiment did not measure
accuracy on unfamiliar layouts, handwriting or real scans.

The [experiment summary](outputs/experiments/SG05/summary.csv) and [browser evidence](docs/merge/M02.md)
include the fixed methods, results and provenance. Verify the saved evidence or
reproduce the study in a new directory with these commands:

```bash
.venv/bin/python docs/merge/verify_m02.py
.venv/bin/python scripts/evaluate_dataset.py --output-dir /tmp/dip042-sg05-repeat
.venv/bin/python -m unittest discover -s tests -v
```

Use fictional samples for the demo. The application does not save uploads by
default, but a downloaded report can contain OCR text. Keep any private files
and reports outside version control.

## Six-minute demo

1. Launch Streamlit with the command above. Upload the four clear fictional
   files listed in the [demo script](docs/demo_script.md), then analyze. With
   the default checklist, the expected result is Ready at 100% for both scores.
2. Open the Income Certificate. Compare the processing stages and OCR results.
3. Remove the Identity Proof and analyze again. The expected result is
   Incomplete, with both scores at 75%. Add the fictional missing-name version
   from the demo script and analyze. Coverage returns to 100% while readiness
   stays at 75% and the status becomes Needs Attention. Download a report.

## Submission files

- Academic report [PDF](docs/project_report.pdf) and [editable DOCX](docs/project_report.docx)
- [PowerPoint presentation](docs/project_042_presentation.pptx)
- [Combined viva Q&A](docs/viva.md) and [demo script](docs/demo_script.md)
- [Full delivery manifest](docs/DELIVERY.md)

## Setup troubleshooting

- `No module named ...`: use this checkout's `.venv/bin/python`, then install
  its `requirements.txt`.
- Venv creation fails: install `python3-venv` using the Ubuntu command above.
- Missing Tesseract or `eng`: install the separate engine/language packages;
  reinstalling Pytesseract alone cannot provide them.
- Package download fails: check network access and retry the install. An
  existing pip version does not prove an attempted upgrade reached the index.
- Repeated `Inotify queue overflowed`: nested worktrees/environments can overload
  recursive watching. The launch command above disables watching; restart the
  server after code changes. This was observed and resolved during M01.
- `pip check` reports conflicts: keep the exact error and resolve it in an
  integration chat; personal tracks must not change shared requirements.

Verified setup versions and real command results are recorded in
`docs/merge/M00.md` and its environment JSON files. Verify each new machine
separately; checks on this machine do not verify a remote student's computer.

## Git history

The combined project is on local `main` and `codex/integration`. The owner
branches preserve both students’ sprint commits. The [merge handoff](MERGE_HANDOFF.md)
records the final local delivery and publication status. Git ignores virtual
environments, nested worktrees, private uploads, caches and local secrets.
