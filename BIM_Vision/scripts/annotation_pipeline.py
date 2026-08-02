import sys
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
    ANNOTATION_IMAGES_PATH,
    ANNOTATION_LABELS_PATH,
    ANNOTATION_EXPORTS_PATH,
)

# Create annotation folders
ANNOTATION_IMAGES_PATH.mkdir(parents=True, exist_ok=True)
ANNOTATION_LABELS_PATH.mkdir(parents=True, exist_ok=True)
ANNOTATION_EXPORTS_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("      BIM Vision Annotation Pipeline")
print("=" * 60)

print("\nStep 1 : Client Data Intake")
print(f"   PDF Folder : {SCANNED_PDF_PATH}")
print(f"   JPG Folder : {PHONE_PHOTOS_PATH}")
print(f"   DWG Folder : {DWG_PATH}")
print(f"   DXF Folder : {DXF_PATH}")

print("\nStep 2 : Preprocessing")
print(f"   PDF  -> {PDF_PREPROCESS_PATH}")
print(f"   JPG  -> {JPG_PREPROCESS_PATH}")
print(f"   DWG  -> {DWG_PREPROCESS_PATH}")
print(f"   DXF  -> {DXF_PREPROCESS_PATH}")

print("\nStep 3 : Annotation")
print(f"   Images Folder : {ANNOTATION_IMAGES_PATH}")
print(f"   Labels Folder : {ANNOTATION_LABELS_PATH}")

print("\nStep 4 : Export")
print(f"   Export Folder : {ANNOTATION_EXPORTS_PATH}")

print("\nPipeline Status : READY")
print("=" * 60)