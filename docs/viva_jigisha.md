# Jigisha's application viva

## Why check document types and fields separately?

A title can tell us what the document is, even if a required value is absent or unreadable. In the frozen missing-name example, OCR reads enough of the page to detect Identity Proof. The configured name field is empty, so that type is present and unusable.

## How does classification work?

The classifier reads the selected OCR text. It folds case and collapses whitespace, then matches whole phrases such as “income certificate” or “mark sheet.” It keeps the matched phrases as evidence. With no matching type it returns Unknown. If different types match, it also returns Unknown and marks the result ambiguous. A filename or a lone word like “income” supplies no type evidence.

## How do regular expressions find fields?

`extract_fields` looks for a supported label and a value after the colon on the same line. It checks the shape of the value. For instance, an issue date must be a valid calendar date written as YYYY-MM-DD, and certificate numbers apply to the two certificate layouts. IDs stay strings, which preserves leading zeros. A conflicting or malformed occurrence leaves the field empty. The UI displays “Not Found / Unreadable” because the selected text may give too little evidence to distinguish causes.

## Which OCR result do the rules use?

The app displays both original and processed OCR. Processed is the initial selection. Changing to original makes classification, extraction and readiness use original text together on the next analysis. The two OCR results are retained separately for comparison.

## What makes a file readable and what makes a type usable?

The demonstration profile calls the selected OCR readable when its status is `ok` and it contains at least 20 letters or digits. A required type is usable when one recognized, readable file of that type contains every configured required field. The count is a heuristic and cannot prove the text is correct. Income and Caste certificates need a student name and certificate number. Marksheet and Identity Proof need a student name.

## How are coverage and readiness calculated?

Coverage is 100 times the number of unique detected required types divided by the number of selected required types. Readiness uses unique usable required types as its numerator. In the four-type missing-name case, coverage is 100 × 4/4 = 100% and readiness is 100 × 3/4 = 75%. The app requires at least one selected type.

## What do the three application statuses mean?

Incomplete means at least one required type is missing. Needs Attention means every required type is detected, but at least one has no usable file. Ready means every selected required type has a usable file. The report lists missing and detected-but-unusable types separately, including when both occur in the same batch.

## What happens when two files have the same name or type?

The app gives each upload an ID based on its position and a hash of its name and bytes. Every file remains in the report, while the same required type earns at most one coverage and one readiness credit. One good copy can satisfy the type. Two partial copies cannot combine their fields to satisfy it.

## How do blank, unrelated and corrupt uploads differ?

In the frozen batch, the blank image reached OCR and returned `no_text`. The unrelated image returned OCR text with no matching title, so its type was Unknown. The corrupt file failed image decoding and retained an error record. Each still counted as a submitted file.

## How do you prevent an old report from appearing current?

`input_signature` includes the uploads in order, processing settings, selected types, OCR source and configuration. When the signature changes, `invalidate_results` clears the stored analysis, including its image views and downloads. The user presses Analyze again. The app saves no upload files by default. Downloading JSON or Markdown creates a separate local copy that can contain OCR text.

## What can the results tell us about preprocessing?

Original and default processed OCR both scored zero pooled CER across the eight fictional images. Some alternatives made OCR worse. For example, global thresholding blanked the faint income sample. The small set includes related derivatives and supports a comparison under fixed settings. General accuracy on unfamiliar documents remains unmeasured.

## What does Ready mean outside the demo?

Ready means the current demonstration checklist has enough readable, labeled information. Official eligibility, document authenticity and whether all documents belong to the same person are outside the app's scope. The title and field rules cover the English sample layouts. Unfamiliar layouts and degraded OCR can leave type or field evidence unresolved.
