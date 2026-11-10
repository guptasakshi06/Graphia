# Project 042 DIP and OCR Viva

**Practice notes for Sakshi Gupta.** The results below come from the [M02 freeze](merge/M02.md). The numerical mini-examples teach the ideas; they are not extra experiments.

1. **Why did you choose this project?**

    An applicant can upload the expected number of files and still miss a required document or an important field. We wanted to show how the condition of an image affects what the computer can recover, then make the checklist explain the missing or unusable items.

2. **Why is this a digital image processing project?**

    We operate on pixels before reading text. Grayscale changes representation, filters process neighborhoods, histograms describe intensities, thresholds segment foreground from background, and morphology changes stroke shapes. OCR is how we observe the effect; classification and readiness are later rule-based steps.

3. **Why grayscale and what is BGR?**

    OpenCV stores a color pixel in blue, green, red order. Grayscale keeps one intensity. For RGB values (100, 150, 200), the weighted sum is 0.299(100) + 0.587(150) + 0.114(200) ≈ 141. It is easier to threshold one channel, but color differences can disappear.

4. **Why cap the image size?**

    A large image costs more memory and processing time. We preserve the aspect ratio and cap the longest side at 1,800 pixels. A 3,600 × 2,400 image would become 1,800 × 1,200. The 1,400 × 1,000 study images did not resize. Too much downsampling can lose small letters.

5. **Gaussian or median filtering?**

    Gaussian smoothing averages nearby pixels with higher weights near the center. It can reduce small intensity fluctuations but blur edges. Median filtering chooses the middle ranked value. In a toy neighborhood of 20, 21, 22, 23, 24, 25, 26, 27 and 255, the median is 24, so one bright outlier has little effect. Both can damage tiny details if the window is too large.

6. **What is a histogram? Why use CLAHE?**

    A histogram counts pixels at each intensity. If the values are [10, 10, 80, 200], the bin at 10 has count two. Global equalization uses the entire image’s cumulative histogram. CLAHE clips histogram peaks in local tiles and blends nearby mappings. We used clip limit 2.0 and an 8 × 8 tile grid; limiting amplification does not guarantee better OCR.

7. **Explain global, Otsu and adaptive thresholding.**

    A global cutoff of 127 puts 100 into black and 160 into white. Otsu picks one cutoff from the histogram: with values grouped near 20 and 220, a cutoff separating the groups keeps their internal variation small. Formally it minimizes the weighted within-group variance. Adaptive Gaussian thresholding picks a cutoff locally; if a weighted neighborhood average is 170 and C is 11, the cutoff there is 159. It helps with uneven lighting but can keep noise.

8. **Explain erosion and dilation. Why invert?**

    We make text the white foreground temporarily. Erosion keeps a pixel only where the structuring element fits in the foreground; dilation adds foreground around strokes. In a toy one-dimensional binary row 0011100, a centered three-pixel element gives 0001000 after erosion and 0111110 after dilation. Our experiment uses a 2 × 2 rectangle and restores dark text afterward.

9. **Opening or closing?**

    Opening erodes then dilates, which can remove isolated foreground dots. Closing dilates then erodes, which can fill small gaps. Opening can remove punctuation or thin strokes; closing can join neighboring letters. We demonstrate both and leave morphology off by default.

10. **What is OCR and how does Tesseract fit?**

     OCR turns image patterns into machine-readable text. Tesseract can preprocess and segment an image, recognize its text with the installed language data and return a transcription. PSM 6 treats the input as one uniform text block. We call Tesseract 5.3.4 locally via Pytesseract with English and a 20-second timeout; we did not train it. A blank result is different from an engine error. The application does not treat confidence as accuracy.

11. **How do you calculate CER? Can it exceed 100%?**

     Find the minimum insertions, deletions and substitutions and divide by reference characters. Comparing `cat` to `car` needs one substitution, so CER is 1/3. When comparing `cat` to `catxxxx`, four insertions give 4/3. Our normalization casefolds and collapses whitespace while keeping punctuation. Exact field matching is a separate check.

12. **What did the experiment show?**

     On eight fictional images from four layouts, both original and default had 0/2,190 normalized edits, 8/8 correct types and 28/28 exact present fields. That is a tie on this dataset. We ran 14 fixed methods across eight images; the original and default were two of those methods. We did not select a best method using the reference text at runtime.

13. **Give examples where processing made OCR worse.**

     Global threshold 127 turned the faint income sample white. It returned no text, so CER was 288/288. Equalization amplified noise on the noisy caste sample: 2,436 edits on 295 characters and an Unknown type. Erosion changed “Application ID” to “Application 1D” there, losing an optional field even though CER was only 1/295. A visibly sharper image or a small CER is not enough to guarantee usable fields.

14. **How does the app identify missing documents?**

     It matches title cues in the selected OCR text, then checks labeled fields for each detected type. A type needs one individually usable candidate; duplicates do not add credit. In the browser’s missing-name case, four types were detected but only three usable: 4/4 gives 100% coverage, 3/4 gives 75% readiness. The Identity Proof was detected and readable by the heuristic but lacked its required name.

15. **What would you improve before making stronger claims?**

     Use independent, consented or reusable scans covering different layouts, blur and lighting. Evaluate changes such as deskew on a held-out set and keep failure cases. Our fictional samples cannot establish general accuracy, and the app does not check authenticity, common applicant identity or official eligibility.

For a demonstration, open the [faint-income threshold figure](../outputs/experiments/SG05/income_certificate_low_contrast/thresholds.png), compare the global and Otsu panels, then explain the original/default tie from the [paired result table](../outputs/experiments/SG05/original_processed.csv).
