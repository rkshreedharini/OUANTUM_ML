import sys
from pathlib import Path

# Add project root
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
    ANNOTATIONS_PATH,
    ANNOTATION_IMAGES_PATH,
    ANNOTATION_LABELS_PATH,
    ANNOTATION_EXPORTS_PATH,
    ANNOTATION_SCHEMAS_PATH,
    ANNOTATION_SCHEMA_FILE,
    LABEL_STUDIO_PATH,
    LABEL_STUDIO_CONFIG,
    LABEL_STUDIO_TASKS,
    LABEL_STUDIO_INFO,
    PREPROCESSING_PATH,
    PDF_PREPROCESS_PATH,
    JPG_PREPROCESS_PATH,
    DWG_PREPROCESS_PATH,
    DXF_PREPROCESS_PATH,
)

print("=" * 60)
print(" MEMBER 3 - ANNOTATION VALIDATION ")
print("=" * 60)

items = [
    ("Annotations Folder", ANNOTATIONS_PATH),
    ("Annotation Images", ANNOTATION_IMAGES_PATH),
    ("Annotation Labels", ANNOTATION_LABELS_PATH),
    ("Annotation Exports", ANNOTATION_EXPORTS_PATH),
    ("Annotation Schemas", ANNOTATION_SCHEMAS_PATH),
    ("annotation_schema.json", ANNOTATION_SCHEMA_FILE),
    ("Label Studio Folder", LABEL_STUDIO_PATH),
    ("config.xml", LABEL_STUDIO_CONFIG),
    ("tasks.json", LABEL_STUDIO_TASKS),
    ("project_info.txt", LABEL_STUDIO_INFO),
    ("Preprocessing Folder", PREPROCESSING_PATH),
    ("PDF Folder", PDF_PREPROCESS_PATH),
    ("JPG Folder", JPG_PREPROCESS_PATH),
    ("DWG Folder", DWG_PREPROCESS_PATH),
    ("DXF Folder", DXF_PREPROCESS_PATH),
]

success = 0

for name, path in items:
    if path.exists():
        print(f"✅ {name:<30} Found")
        success += 1
    else:
        print(f"❌ {name:<30} Missing")

print("=" * 60)
print(f"Validation Completed : {success}/{len(items)} Items Found")
print("=" * 60)

if success == len(items):
    print("🎉 Member 3 setup completed successfully.")
else:
    print("⚠️ Some folders/files are missing.")