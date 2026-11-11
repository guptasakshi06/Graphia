"""Try alternate image inputs for photos while retaining OCR provenance."""

import re

import cv2

from modules.classification import (GRADE_SHEET_HEADING, HINDI_INCOME_HEADING,
                                    SC_CERTIFICATE_HEADING, UP_INCOME_HEADING, classify_document)
from modules.extraction import extract_fields


UP_INCOME_TITLE = "कार्यालय तहसीलदार द्वारा प्रदत्त"
# Relative positions of the printed header, holder block and two distinct
# number rows in the observed UP e-District form. Coordinates use the page
# outline rather than the dimensions of the original camera frame.
UP_REGIONS = {
    "heading": (162, 160, 391, 183),
    "application": (128, 195, 222, 207),
    "certificate": (125, 206, 216, 220),
    "holder": (269, 255, 373, 278),
}
SMALL_NUMBERS = dict(zip(
    "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(),
    range(1, 20),
))
TENS = dict(zip("twenty thirty forty fifty sixty seventy eighty ninety".split(), range(20, 100, 10)))


def _paper_crop(image):
    """Remove background when a single large, bright, low-saturation page is visible."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 0, 160), (180, 35, 255))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image
    page = max(contours, key=cv2.contourArea)
    x, y, width, height = cv2.boundingRect(page)
    total = image.shape[0] * image.shape[1]
    if cv2.contourArea(page) < total * 0.35 or width * height > total * 0.92:
        return image
    return image[y:y + height, x:x + width]


def _read_region(gray, key, scale, read, **engine):
    height, width = gray.shape
    x0, y0, x1, y1 = UP_REGIONS[key]
    region = gray[round(y0 * height / 764):round(y1 * height / 764),
                  round(x0 * width / 520):round(x1 * width / 520)]
    enlarged = cv2.resize(region, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    if key == "certificate" and scale == 4:
        _, enlarged = cv2.threshold(enlarged, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    if key != "heading":
        enlarged = cv2.copyMakeBorder(enlarged, 16, 16, 16, 16, cv2.BORDER_CONSTANT, value=255)
    return read(enlarged, engine)


def _read_band(pixels, box, read, lang, psm, timeout):
    height, width = pixels.shape[:2]
    x0, y0, x1, y1 = box
    region = pixels[int(y0 * height):int(y1 * height), int(x0 * width):int(x1 * width)]
    if not region.size:
        return {"text": ""}
    scale = min(3, 1600 / max(region.shape))
    enlarged = cv2.resize(region, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    return read(enlarged, {"lang": lang, "psm": psm, "timeout": timeout})


def _thousands_in_words(text):
    units = "|".join(SMALL_NUMBERS)
    tens = "|".join(TENS)
    values = []
    for match in re.finditer(
        rf"\b(?:(?P<tens>{tens})(?:[\s-]+(?P<ones>{units}))?|(?P<small>{units}))\s+thousand\b",
        text.casefold(),
    ):
        value = TENS.get(match["tens"], 0) + SMALL_NUMBERS.get(match["ones"] or match["small"], 0)
        values.append(value * 1000)
    return values


def recover_up_income_amounts(image, text, read, timeout):
    """Use the printed amount in words when two reads of this UP layout agree."""
    page = _paper_crop(image)
    if not UP_INCOME_HEADING.search(text):
        heading = _read_band(page, (0, .13, 1, .36), read, "hin+eng", 6, timeout)
        if not UP_INCOME_HEADING.search(heading["text"]):
            return {}
    box = (0, .57, 1, .72) if page.shape[0] / page.shape[1] < 1.35 else (0, .47, 1, .60)
    first, second = (
        _thousands_in_words(_read_band(page, box, read, "eng", psm, timeout)["text"])
        for psm in (6, 11)
    )
    if first == second and len(first) == 2 and first[1] == first[0] * 12:
        return {"annual_income": f"₹{first[1]:,}", "monthly_income": f"₹{first[0]:,}"}
    return {}


def _read_known_header(gray, page_ocr, read, engine):
    """Use a tighter header view for small or framed documents."""
    timeout = engine["timeout"]
    regions = [(GRADE_SHEET_HEADING, (0, 0, 1, .47), "eng", "grade sheet header")]
    if gray.shape[1] <= 650:
        regions.append((SC_CERTIFICATE_HEADING, (.14, .13, .87, .29), "eng", "SC certificate header"))
    if engine["lang"] == "eng+hin":
        regions.append((UP_INCOME_HEADING, (0, .13, 1, .36), "hin+eng", "UP income header"))
    for pattern, box, lang, label in regions:
        header = _read_band(gray, box, read, lang, 6, timeout)
        if match := pattern.search(header["text"]):
            # The grade-sheet crop also contains its labeled holder name.
            if pattern is not GRADE_SHEET_HEADING:
                header = {**header, "text": match.group().strip() + "\n" + page_ocr["text"]}
            yield label, header, None


def _read_up_income(gray, read, page_ocr, timeout):
    """Read separate regions only when the form's exact issuer heading is present."""
    height, width = gray.shape
    if width < 350 or not 1.35 <= height / width <= 1.6:
        return None
    heading = _read_region(gray, "heading", 4, read, lang="hin+eng", psm=6, timeout=timeout)
    title = " ".join(heading["text"].split())
    if not title.startswith(UP_INCOME_TITLE) or not HINDI_INCOME_HEADING.fullmatch(title):
        return None
    recovered = {**page_ocr, "text": heading["text"].rstrip() + "\n" + page_ocr["text"],
                 "status": "ok", "error": None}
    layout = {"student_name": None, "certificate_number": None}
    digits = {"lang": "eng", "psm": 7, "timeout": timeout, "digits_only": True}
    application = _read_region(gray, "application", 4, read, **digits)["text"].strip()
    # Confirm the distinct application row before reading the certificate row.
    if re.fullmatch(r"[0-9]{15}", application):
        number = _read_region(gray, "certificate", 4, read, **digits)["text"].strip()
        check = _read_region(gray, "certificate", 5, read, **digits)["text"].strip()
        if number == check and re.fullmatch(r"[0-9]{12}", number):
            layout["certificate_number"] = number
        holder = _read_region(gray, "holder", 4, read, lang="eng", psm=6, timeout=timeout)
        holder_check = _read_region(gray, "holder", 6, read, lang="eng", psm=6, timeout=timeout)
        name = " ".join(holder["text"].split())
        if name.casefold() == " ".join(holder_check["text"].casefold().split()) and re.fullmatch(
            r"[A-Za-z]+(?:[ '-][A-Za-z]+){1,4}", name
        ):
            layout["student_name"] = name
    return recovered, layout


def _evaluate(ocr, layout_fields=None):
    classification = classify_document(ocr["text"])
    doc_type = classification["doc_type"]
    fields = extract_fields(ocr["text"], doc_type)
    if doc_type == "income_certificate" and layout_fields is not None:
        for key, value in layout_fields.items():
            if value is not None:
                previous = fields[key]
                fields[key] = value if previous is None or previous.casefold() == value.casefold() else None
    recognized = doc_type != "unknown"
    complete = recognized and bool(fields["student_name"]) and (
        doc_type not in ("caste_certificate", "income_certificate") or bool(fields["certificate_number"])
    )
    score = (recognized, complete, sum(value is not None for value in fields.values()),
             ocr["status"] == "ok", min(400, sum(char.isalnum() for char in ocr["text"])))
    return score, classification, fields


def recover_photo(image, original, processed, read, engine):
    """Return the selected OCR result, fields and method for a single upload."""
    selected = max((("original", original), ("processed", processed)),
                   key=lambda candidate: _evaluate(candidate[1])[0])
    source, best = selected
    score, classification, fields = _evaluate(best)
    method = source
    if score[1] or (original["status"] == processed["status"] == "error"):
        return source, best, classification, fields, method

    retry = {**engine, "timeout": min(engine["timeout"], 5)}
    page = _paper_crop(image)
    gray = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)
    factor = min(3, 1800 / max(gray.shape))
    enlarged = cv2.resize(gray, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
    page_ocr = read(enlarged, {**retry, "psm": 4})
    attempts = [("cropped grayscale", page_ocr, None)]
    if engine["lang"] == "eng+hin" and page is not image:
        region_result = _read_up_income(gray, read, page_ocr, retry["timeout"])
        if region_result is not None:
            attempts.append(("UP income form regions", *region_result))
    if not score[0] and not any(classify_document(ocr["text"])["doc_type"] != "unknown" for _, ocr, _ in attempts):
        attempts.extend(_read_known_header(page, page_ocr, read, retry))
    for label, ocr, layout in attempts:
        result = _evaluate(ocr, layout)
        if result[0] > score:
            score, classification, fields = result
            source, best, method = "processed", ocr, label
    if score[1]:
        return source, best, classification, fields, method

    for label, angle in (
        ("rotated 90° left", cv2.ROTATE_90_COUNTERCLOCKWISE),
        ("rotated 90° right", cv2.ROTATE_90_CLOCKWISE),
        ("rotated 180°", cv2.ROTATE_180),
        ("grayscale sparse text", None),
    ):
        pixels = enlarged if angle is None else cv2.rotate(image, angle)
        ocr = read(pixels, {**retry, "psm": 11 if angle is None else 4})
        result = _evaluate(ocr)
        if result[0] > score:
            score, classification, fields = result
            source, best, method = "processed", ocr, label
            if score[1]:
                break
    return source, best, classification, fields, method
