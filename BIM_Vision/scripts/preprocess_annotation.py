import sys
import shutil
from pathlib import Path

# Add project root
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
    SCANNED_PDF_PATH,
    PHONE_PHOTOS_PATH,
    DWG_PATH,
    DXF_PATH,
    PDF_PREPROCESS_PATH,
    JPG_PREPROCESS_PATH,
    DWG_PREPROCESS_PATH,
    DXF_PREPROCESS_PATH,
)

# Create preprocessing folders
PDF_PREPROCESS_PATH.mkdir(parents=True, exist_ok=True)
JPG_PREPROCESS_PATH.mkdir(parents=True, exist_ok=True)
DWG_PREPROCESS_PATH.mkdir(parents=True, exist_ok=True)
DXF_PREPROCESS_PATH.mkdir(parents=True, exist_ok=True)


def copy_files(source, destination):
    count = 0

    if not source.exists():
        return count

    for file in source.iterdir():
        if file.is_file():
            shutil.copy(file, destination / file.name)
            count += 1

    return count


pdf_count = copy_files(SCANNED_PDF_PATH, PDF_PREPROCESS_PATH)
jpg_count = copy_files(PHONE_PHOTOS_PATH, JPG_PREPROCESS_PATH)
dwg_count = copy_files(DWG_PATH, DWG_PREPROCESS_PATH)
dxf_count = copy_files(DXF_PATH, DXF_PREPROCESS_PATH)

print("=" * 50)
print("Preprocessing Completed")
print("=" * 50)

print(f"PDF Files  : {pdf_count}")
print(f"JPG Files  : {jpg_count}")
print(f"DWG Files  : {dwg_count}")
print(f"DXF Files  : {dxf_count}")