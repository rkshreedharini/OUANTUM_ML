import json
from pathlib import Path

OUTPUT = Path("output")

def merge_files():

    # Find every OCR json except geometry and already merged files
    ocr_files = [
        f for f in OUTPUT.glob("*.json")
        if "_geometry" not in f.stem and "_bim" not in f.stem
    ]

    for ocr_file in ocr_files:

        # Remove ".jpg" from filename if present
        house_name = ocr_file.stem.replace(".jpg", "").replace(".jpeg", "").replace(".png", "")

        geometry_file = OUTPUT / f"{house_name}_geometry.json"

        if not geometry_file.exists():
            print(f"Skipping {ocr_file.name} (geometry not found)")
            continue

        with open(ocr_file, "r") as f:
            ocr = json.load(f)

        with open(geometry_file, "r") as f:
            geometry = json.load(f)

        final_data = {
            "house": house_name,
            "rooms": ocr.get("rooms", []),
            "dimensions": ocr.get("dimensions", []),
            "geometry": geometry
        }

        out = OUTPUT / f"{house_name}_bim.json"

        with open(out, "w") as f:
            json.dump(final_data, f, indent=4)

        print(f"Created {out.name}")

if __name__ == "__main__":
    merge_files()