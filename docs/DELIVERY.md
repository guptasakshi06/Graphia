# Project 042 Delivery Manifest

**Document Intelligence for Application Readiness and Missing-Requirement Detection**

**Sakshi Gupta and Jigisha Baiswar**

The technical package was verified at M03. Use the local `main` or `codex/integration` checkout for delivery.

| Brief item | Delivered file or directory |
|---|---|
| 1. Python source | [modules](../modules/), [scripts](../scripts/) |
| 2. Dependencies | [requirements.txt](../requirements.txt), [verified dependency snapshot](merge/M00-requirements-lock.txt) |
| 3. Project structure | [README folder layout](../README.md#folder-layout-and-local-launch), [team contract](../TEAM_CONTRACT.md) |
| 4. Sample dataset | [Eight fictional images, reference text and provenance](../dataset/README.md), [manifest](../dataset/manifest.json), [visual review](../dataset/visual_review.json) |
| 5. Streamlit application | [app.py](../app.py), [demonstration checklist](../config/requirements.json) |
| 6. Experiment and browser captures | [DIP experiment figures](../outputs/experiments/SG05/), [15 actual browser screenshots](../outputs/screenshots/JB05/) |
| 7. Before-and-after comparisons | [Seven comparison groups and figure paths](validation/sakshi.md#all-seven-comparison-groups-and-fixed-settings), [example threshold figure](../outputs/experiments/SG05/income_certificate_low_contrast/thresholds.png) |
| 8. Experimental results | [Method summary](../outputs/experiments/SG05/summary.csv), [paired OCR results](../outputs/experiments/SG05/original_processed.csv), [browser downloads](../outputs/reports/JB05/) |
| 9. README | [Ubuntu setup, launch, troubleshooting and demo](../README.md) |
| 10. College report | [PDF](project_report.pdf), [editable DOCX](project_report.docx), [Markdown source](project_report.md) |
| 11. Presentation | [12-slide PowerPoint](project_042_presentation.pptx), [outline](presentation_outline.md) |
| 12. System architecture | [PNG](diagrams/architecture.png), [editable SVG](diagrams/architecture.svg) |
| 13. Workflow | [PNG](diagrams/workflow.png), [editable SVG](diagrams/workflow.svg) |
| 14. Viva questions and answers | [Combined viva](viva.md), [DIP/OCR source](viva_sakshi.md), [application source](viva_jigisha.md), [demo script](demo_script.md) |

The [M03 verification record](merge/M03.md) documents 107 passing tests, a fresh real-Tesseract smoke test, 387 verified M02 evidence files, and review of all 10 report pages and 12 slides. M03 reuses the saved M02 browser evidence. The tracked delivery excludes private uploads, virtual environments and nested worktree copies.

To run the demo from the repository root after [Ubuntu setup](../README.md#ubuntu-setup):

```bash
.venv/bin/python -m streamlit run app.py --server.address=127.0.0.1 --server.fileWatcherType=none --browser.gatherUsageStats=false
```

Open the local URL and follow the [demo script](demo_script.md) with the fictional files. The measured zero-CER tie covers eight related fictional samples. The English title and label rules can leave unfamiliar layouts unresolved. The configured readiness score describes usable checklist information. Authenticity, official eligibility and applicant identity matching are outside its scope.

Before college submission, fill in both roll numbers, the college and department names, and the faculty guide. Apply the prescribed cover format if required and export the updated report PDF. The technical verification used LibreOffice for both Office formats. Student walkthrough, college submission and a live mock viva remain separate activities.
