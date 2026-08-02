import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
    SCANNED_PDF_PATH,
    PHONE_PHOTOS_PATH,
    DWG_PATH,
    DXF_PATH
)

folders = [
    SCANNED_PDF_PATH,
    PHONE_PHOTOS_PATH,
    DWG_PATH,
    DXF_PATH
]

print("=" * 40)
print("Creating Client Data Folders")
print("=" * 40)

for folder in folders:
    folder.mkdir(parents=True, exist_ok=True)
    print(f"Created: {folder}")

print("\nAll folders are ready.")