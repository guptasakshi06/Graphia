# Project 042 demo script

Use the completed M02 baseline or the verified final integration checkout. Run the commands from that checkout's repository root with its own prepared virtual environment.

```bash
.venv/bin/python scripts/check_environment.py
.venv/bin/python -m streamlit run app.py --server.headless=true --server.address=127.0.0.1 --server.port=8505 --server.fileWatcherType=none --browser.gatherUsageStats=false
```

Open [the local app](http://127.0.0.1:8505) in a browser. The walkthrough below uses the four default checklist types and the default processed OCR source. Use only the repository's fictional inputs.

## Six-minute walkthrough

1. **Jigisha, 45 seconds.** Introduce the demonstration checklist and upload the four clear images below. Open one upload preview, then press **Analyze documents**.

   ```text
   dataset/income_certificate/income_certificate_clear.png
   dataset/caste_certificate/caste_certificate_clear.png
   dataset/marksheet/marksheet_clear.png
   dataset/identity_proof/identity_proof_clear.png
   ```

2. **Sakshi, 90 seconds.** Open the Income Certificate result. Show the original image, grayscale and threshold views, then compare the original and processed OCR panels. Explain the default median kernel of 3, CLAHE, Otsu and disabled morphology. In the saved [threshold comparison](../outputs/experiments/SG05/income_certificate_low_contrast/thresholds.png), point to the white global-threshold result and legible Otsu result. The original and default OCR tie at pooled CER 0 on the eight fictional images.
3. **Jigisha, 75 seconds.** Show the matched income title and extracted name and certificate number. Return to the summary. The frozen complete run shows four files, four detected and four usable types, Ready at 100% coverage and readiness.
4. **Jigisha, 90 seconds.** Remove the clear Identity Proof. Wait for the old results and downloads to disappear, then analyze. The frozen missing case has 75% coverage and readiness and is Incomplete. Add `outputs/reports/JB05/inputs/JB05_FICTIONAL_identity_missing_name.png` in place of the clear Identity Proof. Analyze again. The frozen result has 100% coverage and 75% readiness and is Needs Attention. Point out the detected-but-unusable Identity Proof and empty name.
5. **Both, 60 seconds.** Download a JSON or Markdown report. Jigisha explains why duplicate uploads do not increase either percentage. Sakshi closes with the small synthetic sample limit. Both describe Ready as a result for the selected demonstration checklist.

## Recovery

- For a connection error, return to the terminal, stop the task's server with Ctrl-C if it is still running, and rerun the launch command. If port 8505 is already occupied by another process, use port 8506 and open that port in the browser. Reload, reselect the fictional files and analyze again. The frozen JB05 session had one interruption and completed its settings scenario after restarting.
- If the OCR engine is unavailable, run `.venv/bin/python scripts/check_environment.py`, `tesseract --version` and `tesseract --list-langs`. Check the repository setup instructions and confirm English `eng` data before retrying. If source files changed, restart because the file watcher is disabled.
- If results clear after a widget change, confirm uploads and a nonempty checklist, then press **Analyze documents**. If one image fails decoding, open its error record and reselect the intended PNG or JPEG.
- If the live demo remains unavailable, use the saved [Ready capture](../outputs/screenshots/JB05/05_complete_ready.jpg), [Needs Attention capture](../outputs/screenshots/JB05/07_detected_unusable.jpg) and [complete Markdown download](../outputs/reports/JB05/complete.md). Identify them as saved JB05 evidence.

## Cross-teaching checklist

- Sakshi can explain title ambiguity, label-based fields and why 4/4 detected with 3/4 usable gives 100% coverage and 75% readiness.
- Jigisha can explain why thresholding changes OCR input, how the original/processed comparison is controlled, and why the zero-CER tie only describes this sample set.
- Both can launch and recover the app, locate the frozen evidence and explain the limits on eligibility, authenticity and identity matching.
