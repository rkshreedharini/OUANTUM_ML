import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import (
    SCANNED_PDF_PATH,
    PHONE_PHOTOS_PATH,
    DWG_PATH,
    DXF_PATH
)

folders = {
    "Scanned PDF": SCANNED_PDF_PATH,
    "Phone Photos": PHONE_PHOTOS_PATH,
    "DWG": DWG_PATH,
    "DXF": DXF_PATH
}

print("=" * 40)
print("Client Data Validation")
print("=" * 40)

for name, folder in folders.items():

    if folder.exists():

        files = list(folder.iterdir())

        print(f"{name:<20}: {len(files)} file(s)")

    else:

        print(f"{name:<20}: Folder Missing")