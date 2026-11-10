# Project 042: Document Intelligence for Application Readiness

Students: **Sakshi Gupta** and **Jigisha Baiswar**.

This local Python project demonstrates image preprocessing, Tesseract OCR,
rule-based document classification, field extraction and a configurable
demonstration scholarship checklist. Readiness describes the configured
presence and usable information only. It does not establish authenticity,
official eligibility or whether documents belong to the same person.

M01 integrates both students’ build tracks with real local Tesseract OCR. Final
dataset evaluation and browser scenario evidence remain for SG05/JB05 and M02.
Read `MERGE_HANDOFF.md` for checkpoint evidence and `HANDOFF.md` for the schedule.

## Ubuntu setup

The project folder is already the integration checkout; do not create a nested
application directory here. On a new computer, choose a directory for a real
copy of this repository before following these commands. The repository is
[guptasakshi06/Graphia](https://github.com/guptasakshi06/Graphia); `origin` uses `https://github.com/guptasakshi06/Graphia.git`.

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
Later merge gates must reconcile that snapshot if dependencies change.

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

Use the handoff inside your own checkout for future personal chats:

- Sakshi: `worktrees/sakshi/SAKSHI_HANDOFF.md`, next SG05 after M01 synchronization.
- Jigisha: `worktrees/jigisha/JIGISHA_HANDOFF.md`, next JB05 after M01 synchronization.
- Integration: root `MERGE_HANDOFF.md`, next M02 after SG05 and JB05.

During personal work, update only owned files and the owner's handoff. The root
personal files are integration snapshots. `TEAM_CONTRACT.md` v1 defines public
functions, options and report keys. Sakshi owns image loading/preprocessing and
OCR. Jigisha owns classification, extraction, readiness, reports and the UI.
Both continue independently from the synchronized M01 baseline. Fixture tests
are development evidence only; M01 additionally verified actual OCR and browser uploads.

At merge checkpoints, record clean intended branch tips, merge locally, test,
and forward-merge integration into both clean personal branches. The initial
GitHub publication was explicitly requested by the user; later pushes/publication
still require user instructions. See `MERGE_HANDOFF.md` for the merge procedure.

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

M01 evidence and real downloads: `docs/merge/M01.md`. SG02–SG04 experiment
artifacts are preliminary; SG05/JB05 validate the integrated behavior before
M02 freezes evidence. Related synthetic derivatives do not prove general OCR
accuracy. Academic report, slides and final submission assembly remain gated.
Use fictional/reusable samples. Keep private files under ignored
`private_uploads/` if needed; do not commit uploads or environments. Selected
public outputs and documentation are intentionally tracked.

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

## GitHub repository and branches

The user requested initial publication on 2026-11-10 to
[guptasakshi06/Graphia](https://github.com/guptasakshi06/Graphia). At the user's request, setup is published as **one commit named `M00`**.
The three intermediate setup commits were replaced in the branch histories. `main` is the GitHub landing branch. Day-to-day development
continues in `codex/integration`, `codex/sakshi-dip` and `codex/jigisha-app` in
the existing separate checkouts. No local branch was renamed or switched.

Handoffs, the public API contract, requirements, source and selected verification
records are tracked. `.gitignore` excludes virtual environments, nested worktree
folders, private uploads, caches and secrets. Each personal branch contains its
own normal project files; the ignored nested folders are not committed as
duplicate copies. Later commits can be published when requested, from the
appropriate branch. M01 is integrated locally; no new push or main update is
part of this checkpoint. Both full tracks and final M03 must finish first.
