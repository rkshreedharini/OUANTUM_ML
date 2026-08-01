import json
from pathlib import Path

from config import IMAGE_DIR, OUTPUT_DIR
from ocr_engine import extract_text
from parser import extract_rooms, extract_dimensions, detect_scale

print("Starting OCR + Parsing...\n")

images = sorted(
    list(IMAGE_DIR.glob("*.jpg")) +
    list(IMAGE_DIR.glob("*.jpeg")) +
    list(IMAGE_DIR.glob("*.png"))
)

for image in images:

    print(f"Processing {image.name}")

    # OCR
    text = extract_text(str(image))

    # Save raw OCR text
    with open(OUTPUT_DIR / f"{image.stem}.txt", "w", encoding="utf-8") as f:
        f.write(text)

    # Parse OCR text
    rooms = extract_rooms(text)
    dimensions = extract_dimensions(text)
    scale = detect_scale(text)

    # Save structured JSON
    data = {
        "house": image.stem,
        "rooms": rooms,
        "dimensions": dimensions,
        "scale": scale
    }

    with open(OUTPUT_DIR / f"{image.stem}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

print("\n✅ OCR and parsing completed!")
print("Results saved in the output folder.")