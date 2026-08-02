from config import (
    PROJECT_NAME,

    # Member 1
    CUBICASA5K_HIGH_QUALITY,
    CUBICASA5K_COLORFUL,
    R2V_IMAGE_PATH,
    R2V_PREDICTION_PATH,

    # Member 2
    CLIENT_DATA_PATH,
    SCANNED_PDF_PATH,
    PHONE_PHOTOS_PATH,
    DWG_PATH,
    DXF_PATH,
    METADATA_FILE,
)

def check_path(name, path):
    if path.exists():
        print(f"✅ {name}")
        print(f"   Path: {path}\n")
    else:
        print(f"❌ {name}")
        print(f"   Path: {path}\n")


def main():

    print("=" * 60)
    print(f"              {PROJECT_NAME}")
    print("=" * 60)

    # ==========================================
    # Member 1
    # ==========================================
    print("\nMember 1 - Public Dataset Verification\n")

    check_path("CubiCasa5K - High Quality", CUBICASA5K_HIGH_QUALITY)
    check_path("CubiCasa5K - Colorful", CUBICASA5K_COLORFUL)

    check_path("R2V - Floorplan Images", R2V_IMAGE_PATH)
    check_path("R2V - Representation Prediction", R2V_PREDICTION_PATH)

    # ==========================================
    # Member 2
    # ==========================================
    print("\nMember 2 - Client Data Verification\n")

    check_path("Client Data Folder", CLIENT_DATA_PATH)
    check_path("Scanned PDF Folder", SCANNED_PDF_PATH)
    check_path("Phone Photos Folder", PHONE_PHOTOS_PATH)
    check_path("DWG Folder", DWG_PATH)
    check_path("DXF Folder", DXF_PATH)
    check_path("Metadata File", METADATA_FILE)

    print("=" * 60)
    print("Project verification completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()

    # ==========================================================
# MEMBER 3 - ANNOTATION TOOLING OWNER
# ==========================================================

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

print("\n==============================")
print(" MEMBER 3 - ANNOTATION TOOL ")
print("==============================")

member3_items = [
    ("Annotations Folder", ANNOTATIONS_PATH),
    ("Annotation Images", ANNOTATION_IMAGES_PATH),
    ("Annotation Labels", ANNOTATION_LABELS_PATH),
    ("Annotation Exports", ANNOTATION_EXPORTS_PATH),
    ("Annotation Schemas", ANNOTATION_SCHEMAS_PATH),
    ("Annotation Schema", ANNOTATION_SCHEMA_FILE),
    ("Label Studio Folder", LABEL_STUDIO_PATH),
    ("Label Studio Config", LABEL_STUDIO_CONFIG),
    ("Label Studio Tasks", LABEL_STUDIO_TASKS),
    ("Project Info", LABEL_STUDIO_INFO),
    ("Preprocessing Folder", PREPROCESSING_PATH),
    ("PDF Preprocessing", PDF_PREPROCESS_PATH),
    ("JPG Preprocessing", JPG_PREPROCESS_PATH),
    ("DWG Preprocessing", DWG_PREPROCESS_PATH),
    ("DXF Preprocessing", DXF_PREPROCESS_PATH),
]

for name, path in member3_items:
    status = "✅ Found" if path.exists() else "❌ Missing"
    print(f"{name:<30}: {status}")

    # ============================================================
# MEMBER 4 - ACTIVE LEARNING LOOP
# ============================================================

from config import (
    FEEDBACK_PATH,
    REVIEW_QUEUE_PATH,
    CORRECTIONS_PATH,
    TRAINING_STORE_PATH,
    FEEDBACK_LOGS_PATH,
    REVIEW_QUEUE_FILE,
    CORRECTIONS_FILE,
    TRAINING_DATA_FILE,
    FEEDBACK_PIPELINE_DOC,
    FEEDBACK_SUMMARY,
)

print("\n")
print("=" * 30)
print(" MEMBER 4 - ACTIVE LEARNING LOOP ")
print("=" * 30)

member4_items = [
    ("Feedback Folder", FEEDBACK_PATH),
    ("Review Queue", REVIEW_QUEUE_PATH),
    ("Corrections Folder", CORRECTIONS_PATH),
    ("Training Store", TRAINING_STORE_PATH),
    ("Logs Folder", FEEDBACK_LOGS_PATH),
    ("Review Queue File", REVIEW_QUEUE_FILE),
    ("Corrections File", CORRECTIONS_FILE),
    ("Training Data File", TRAINING_DATA_FILE),
    ("Feedback Pipeline Doc", FEEDBACK_PIPELINE_DOC),
    ("Feedback Summary", FEEDBACK_SUMMARY),
]

for name, path in member4_items:
    status = "✅ Found" if path.exists() else "❌ Missing"
    print(f"{name:<30}: {status}")