"""OCR-based screenshot scanning and image redaction."""
import re
from collections import Counter
from PIL import Image, ImageDraw
from privacy_scanner import PATTERNS, scan_text

def scan_image(image: Image.Image) -> dict:
    try:
        import pytesseract
        from pytesseract import Output
    except ImportError as exc:
        raise RuntimeError("OCR library is missing. Install dependencies with: pip install -r requirements.txt") from exc

    try:
        data = pytesseract.image_to_data(image, output_type=Output.DICT)
    except Exception as exc:
        raise RuntimeError(
            "Tesseract OCR could not run. Install the Tesseract OCR application for your operating system, "
            "then restart the app. See README.md for instructions."
        ) from exc

    words = []
    for i, word in enumerate(data["text"]):
        word = (word or "").strip()
        if word:
            words.append({
                "text": word,
                "left": int(data["left"][i]),
                "top": int(data["top"][i]),
                "width": int(data["width"][i]),
                "height": int(data["height"][i]),
                "block": data["block_num"][i],
                "line": data["line_num"][i],
            })

  
    grouped = {}
    for word in words:
        key = (word["block"], word["line"])
        grouped.setdefault(key, []).append(word)

    detected_lines = []
    boxes = []
    for line_words in grouped.values():
        line_text = " ".join(w["text"] for w in line_words)
        result = scan_text(line_text)
        if result["findings"]:
            detected_lines.append((line_text, result))
            x1 = min(w["left"] for w in line_words)
            y1 = min(w["top"] for w in line_words)
            x2 = max(w["left"] + w["width"] for w in line_words)
            y2 = max(w["top"] + w["height"] for w in line_words)
            boxes.append((x1, y1, x2, y2))

    combined_text = "\n".join(line for line, _ in detected_lines)
    overall = scan_text(combined_text)
    return {
        "score": overall["score"],
        "level": overall["level"],
        "findings": overall["findings"],
        "boxes": boxes,
    }

def redact_image(image: Image.Image, boxes: list) -> Image.Image:
    protected = image.copy().convert("RGB")
    draw = ImageDraw.Draw(protected)
    for x1, y1, x2, y2 in boxes:
        
        margin = 5
        draw.rectangle(
            (max(0, x1 - margin), max(0, y1 - margin),
             min(protected.width, x2 + margin), min(protected.height, y2 + margin)),
            fill="black"
        )
    return protected
