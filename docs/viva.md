# Project 042 Viva Questions and Answers

Sakshi Gupta leads the DIP and OCR explanation. Jigisha Baiswar leads the application and readiness explanation. Both should be able to walk through the same upload from pixels to report. The examples use [frozen M02 evidence](merge/M02.md) and small arithmetic exercises.

## Digital image processing and OCR

### Why did you choose this project?

An applicant can upload the expected number of files and still miss a required document or an important field. We wanted to show how the condition of an image affects what the computer can recover, then make the checklist explain the missing or unusable items.

### Why is this a digital image processing project?

We operate on pixels before reading text. Grayscale changes representation, filters process neighborhoods, histograms describe intensities, thresholds segment foreground from background, and morphology changes stroke shapes. OCR is how we observe the effect; classification and readiness are later rule-based steps.

### Why grayscale and what is BGR?

OpenCV stores a color pixel in blue, green, red order. Grayscale keeps one intensity. For RGB values (100, 150, 200), the weighted sum is 0.299(100) + 0.587(150) + 0.114(200) ≈ 141. It is easier to threshold one channel, but color differences can disappear.

### Why cap the image size?

A large image costs more memory and processing time. We preserve the aspect ratio and cap the longest side at 1,800 pixels. A 3,600 × 2,400 image would become 1,800 × 1,200. The 1,400 × 1,000 study images did not resize. Too much downsampling can lose small letters.

### Gaussian or median filtering?

Gaussian smoothing averages nearby pixels with higher weights near the center. It can reduce small intensity fluctuations but blur edges. Median filtering chooses the middle ranked value. In a toy neighborhood of 20, 21, 22, 23, 24, 25, 26, 27 and 255, the median is 24, so one bright outlier has little effect. Both can damage tiny details if the window is too large.

### What is a histogram? Why use CLAHE?

A histogram counts pixels at each intensity. If the values are [10, 10, 80, 200], the bin at 10 has count two. Global equalization uses the entire image’s cumulative histogram. CLAHE clips histogram peaks in local tiles and blends nearby mappings. We used clip limit 2.0 and an 8 × 8 tile grid; limiting amplification does not guarantee better OCR.

### Explain global, Otsu and adaptive thresholding.

A global cutoff of 127 puts 100 into black and 160 into white. Otsu picks one cutoff from the histogram: with values grouped near 20 and 220, a cutoff separating the groups keeps their internal variation small. Formally it minimizes the weighted within-group variance. Adaptive Gaussian thresholding picks a cutoff locally; if a weighted neighborhood average is 170 and C is 11, the cutoff there is 159. It helps with uneven lighting but can keep noise.

### Explain erosion and dilation. Why invert?

We make text the white foreground temporarily. Erosion keeps a pixel only where the structuring element fits in the foreground; dilation adds foreground around strokes. In a toy one-dimensional binary row 0011100, a centered three-pixel element gives 0001000 after erosion and 0111110 after dilation. Our experiment uses a 2 × 2 rectangle and restores dark text afterward.

### Opening or closing?

Opening erodes then dilates, which can remove isolated foreground dots. Closing dilates then erodes, which can fill small gaps. Opening can remove punctuation or thin strokes; closing can join neighboring letters. We demonstrate both and leave morphology off by default.

### What is OCR and how does Tesseract fit?

OCR turns image patterns into machine-readable text. Tesseract can preprocess and segment an image, recognize its text with the installed language data and return a transcription. PSM 6 treats the input as one uniform text block. We call Tesseract 5.3.4 locally via Pytesseract with English and a 20-second timeout; we did not train it. A blank result is different from an engine error. The application does not treat confidence as accuracy.

### How do you calculate CER? Can it exceed 100%?

Find the minimum insertions, deletions and substitutions and divide by reference characters. Comparing `cat` to `car` needs one substitution, so CER is 1/3. When comparing `cat` to `catxxxx`, four insertions give 4/3. Our normalization casefolds and collapses whitespace while keeping punctuation. Exact field matching is a separate check.

### What did the experiment show?

On eight fictional images from four layouts, both original and default had 0/2,190 normalized edits, 8/8 correct types and 28/28 exact present fields. That is a tie on this dataset. We ran 14 fixed methods across eight images; the original and default were two of those methods. We did not select a best method using the reference text at runtime.

### Give examples where processing made OCR worse.

Global threshold 127 turned the faint income sample white. It returned no text, so CER was 288/288. Equalization amplified noise on the noisy caste sample: 2,436 edits on 295 characters and an Unknown type. Erosion changed “Application ID” to “Application 1D” there, losing an optional field even though CER was only 1/295. A visibly sharper image or a small CER is not enough to guarantee usable fields.

## Classification, extraction and readiness

### How does classification work?

The classifier reads the selected OCR text. It folds case and collapses whitespace, then matches whole phrases such as “income certificate” or “mark sheet.” It keeps the matched phrases as evidence. With no matching type it returns Unknown. If different types match, it also returns Unknown and marks the result ambiguous. A filename or a lone word like “income” supplies no type evidence.

### How do regular expressions find fields?

`extract_fields` looks for a supported label and a value after the colon on the same line. It checks the shape of the value. For instance, an issue date must be a valid calendar date written as YYYY-MM-DD, and certificate numbers apply to the two certificate layouts. IDs stay strings, which preserves leading zeros. A conflicting or malformed occurrence leaves the field empty. The UI displays “Not Found / Unreadable” because the selected text may give too little evidence to distinguish causes.

### Which OCR result do the rules use?

The app displays both original and processed OCR. Processed is the initial selection. Changing to original makes classification, extraction and readiness use original text together on the next analysis. The two OCR results are retained separately for comparison.

### What makes a file readable and what makes a type usable?

The demonstration profile calls the selected OCR readable when its status is `ok` and it contains at least 20 letters or digits. A required type is usable when one recognized, readable file of that type contains every configured required field. The count is a heuristic and cannot prove the text is correct. Income and Caste certificates need a student name and certificate number. Marksheet and Identity Proof need a student name.

### How are coverage and readiness calculated?

Coverage is 100 times the number of unique detected required types divided by the number of selected required types. Readiness uses unique usable required types as its numerator. In the four-type missing-name case, coverage is 100 × 4/4 = 100% and readiness is 100 × 3/4 = 75%. The app requires at least one selected type.

### What do the three application statuses mean?

Incomplete means at least one required type is missing. Needs Attention means every required type is detected, but at least one has no usable file. Ready means every selected required type has a usable file. The report lists missing and detected-but-unusable types separately, including when both occur in the same batch.

### What happens when two files have the same name or type?

The app gives each upload an ID based on its position and a hash of its name and bytes. Every file remains in the report, while the same required type earns at most one coverage and one readiness credit. One good copy can satisfy the type. Two partial copies cannot combine their fields to satisfy it.

### How do blank, unrelated and corrupt uploads differ?

In the frozen batch, the blank image reached OCR and returned `no_text`. The unrelated image returned OCR text with no matching title, so its type was Unknown. The corrupt file failed image decoding and retained an error record. Each still counted as a submitted file.

### How do you prevent an old report from appearing current?

`input_signature` includes the uploads in order, processing settings, selected types, OCR source and configuration. When the signature changes, `invalidate_results` clears the stored analysis, including its image views and downloads. The user presses Analyze again. The app saves no upload files by default. Downloading JSON or Markdown creates a separate local copy that can contain OCR text.

## Shared questions

### Why can a detected document still leave the application unready?

A title can identify a document even when a required field is empty. In the saved missing-name run, OCR met the readability heuristic and the title identified Identity Proof. The required name was missing. Four types were detected and only three were usable. The report shows 100% coverage, 75% readiness and Needs Attention.

### What does Ready mean in this project?

Ready means the current demonstration checklist has enough readable, labeled information. Official eligibility, document authenticity and whether all documents belong to the same person are outside the app's scope. The title and field rules cover the English sample layouts. Unfamiliar layouts and degraded OCR can leave type or field evidence unresolved.

### What would you improve before making stronger claims?

Use independent, consented or reusable scans covering different layouts, blur and lighting. Evaluate changes such as deskew on a held-out set and keep failure cases. Our fictional samples cannot establish general accuracy, and the app does not check authenticity, common applicant identity or official eligibility.

Use the [demo script](demo_script.md) to practice the handoff between image processing and the application rules.
