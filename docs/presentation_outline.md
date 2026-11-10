# Project 042 presentation outline

**Document Intelligence for Application Readiness and Missing-Requirement Detection**

**Sakshi Gupta and Jigisha Baiswar**

The companion PowerPoint is [project_042_presentation.pptx](project_042_presentation.pptx). Use the frozen M02 evidence and the fictional demonstration checklist throughout.

| Slide | Topic | Speaker and point to make | Evidence |
|---|---|---|---|
| 1 | Project title | Both introduce themselves and identify the local academic demonstration. | [Project brief](../PROJECT_BRIEF.md) |
| 2 | Demonstration checklist | Jigisha names the four types and explains why a submitted file may still leave a requirement unmet. | [Checklist configuration](../config/requirements.json) |
| 3 | System architecture | Sakshi traces decode, preprocessing and the two Tesseract calls. Jigisha follows selected text through rules, fields and reporting. | [Architecture](diagrams/architecture.png), [app](../app.py) |
| 4 | Application workflow | Jigisha explains the status decision in order, retained per-file errors and the need to analyze again after an input change. | [Workflow](diagrams/workflow.png), [readiness implementation](../modules/readiness.py) |
| 5 | Image preprocessing | Sakshi explains the default and compares the thresholds on the faint income certificate. The global threshold produced no text for this image. | [Threshold comparison](../outputs/experiments/SG05/income_certificate_low_contrast/thresholds.png) |
| 6 | OCR, keywords and fields | Sakshi explains both OCR passes. Jigisha shows how the selected text supplies a title phrase and labeled fields. | [Single-file download](../outputs/reports/JB05/single.json), [OCR and fields capture](../outputs/screenshots/JB05/03_ocr_fields.jpg) |
| 7 | Coverage and readiness | Jigisha computes 4/4 and 3/4, and explains the single-candidate rule and duplicate handling. | [Unusable case](../outputs/reports/JB05/unusable.json) |
| 8 | Measured OCR results | Sakshi defines pooled CER, gives the original/default tie, and contrasts three alternatives. | [SG05 summary](../outputs/experiments/SG05/summary.csv), [M02 record](merge/M02.md) |
| 9 | Browser results | Jigisha compares the complete and missing-name cases using the actual captures. | [Complete](../outputs/screenshots/JB05/05_complete_ready.jpg), [Needs Attention](../outputs/screenshots/JB05/07_detected_unusable.jpg) |
| 10 | Browser edge cases | Jigisha walks through missing identity, the nine-file batch and the session checklist subset. | [Frozen browser downloads](../outputs/reports/JB05/) |
| 11 | Evidence and scope limits | Both explain the small related sample set, layout-specific rules and the limits of a checklist decision. | [M02 record](merge/M02.md) |
| 12 | Demo sequence | Both hand over at the OCR panels, then show one missing and one detected-but-unusable case before exporting. | [Demo script](demo_script.md) |

The eight images represent four fictional layouts and four related derivatives. Seven comparison groups cover original/grayscale, Gaussian/median, original/equalization/CLAHE, global/Otsu/adaptive, erosion/dilation, opening/closing and original/default OCR. The [M02 record](merge/M02.md) links the full figures and method results. OCR and browser claims refer to the frozen SG05 and JB05 executions.
