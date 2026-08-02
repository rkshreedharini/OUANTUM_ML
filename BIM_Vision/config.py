from pathlib import Path

# ======================================
# Project Information
# ======================================
PROJECT_NAME = "BIM Vision"

# ======================================
# Base Directory
# ======================================
BASE_DIR = Path(r"E:\BIM_Vision")

# ======================================
# CubiCasa5K Dataset
# ======================================
CUBICASA5K_PATH = BASE_DIR / "datasets" / "CubiCasa5K" / "cubicasa5k"

CUBICASA5K_HIGH_QUALITY = CUBICASA5K_PATH / "high_quality"
CUBICASA5K_COLORFUL = CUBICASA5K_PATH / "colorful"
CUBICASA5K_HIGH_QUALITY_ARCHITECTURAL = CUBICASA5K_PATH / "high_quality_architectural"

# ======================================
# R2V Dataset
# ======================================
R2V_PATH = BASE_DIR / "datasets" / "R2V_R3D"

R2V_IMAGE_PATH = R2V_PATH / "vector_graphics_floorplans" / "floorplan_image"
R2V_PREDICTION_PATH = R2V_PATH / "vector_graphics_floorplans" / "representation_prediction"

# ======================================
# Project Folders
# ======================================
DOCS_PATH = BASE_DIR / "docs"
SCRIPTS_PATH = BASE_DIR / "scripts"
OUTPUTS_PATH = BASE_DIR / "outputs"
MODELS_PATH = BASE_DIR / "models"
NOTEBOOKS_PATH = BASE_DIR / "notebooks"
CONFIGS_PATH = BASE_DIR / "configs"
TESTS_PATH = BASE_DIR / "tests"
# ======================================
# Member 2 - Client Data
# ======================================
CLIENT_DATA_PATH = BASE_DIR / "datasets" /"client_data"

SCANNED_PDF_PATH = CLIENT_DATA_PATH / "scanned_pdf"
PHONE_PHOTOS_PATH = CLIENT_DATA_PATH / "phone_photos"
DWG_PATH = CLIENT_DATA_PATH / "dwg"
DXF_PATH = CLIENT_DATA_PATH / "dxf"

METADATA_FILE = CLIENT_DATA_PATH / "intake_metadata.csv"

# ======================================
# Member 2 Documents
# ======================================
INTAKE_STANDARD_DOC = DOCS_PATH / "intake_standard.md"
DATA_SHARING_DOC = DOCS_PATH / "data_sharing_agreement.md"

# ======================================
# Member 2 Output
# ======================================
INTAKE_SUMMARY = OUTPUTS_PATH / "intake_summary.csv"

# ==========================================================
# MEMBER 3 - ANNOTATION TOOLING OWNER
# ==========================================================

# Annotation Folder
ANNOTATIONS_PATH = BASE_DIR / "annotations"

ANNOTATION_IMAGES_PATH = ANNOTATIONS_PATH / "images"
ANNOTATION_LABELS_PATH = ANNOTATIONS_PATH / "labels"
ANNOTATION_EXPORTS_PATH = ANNOTATIONS_PATH / "exports"
ANNOTATION_SCHEMAS_PATH = ANNOTATIONS_PATH / "schemas"

ANNOTATION_SCHEMA_FILE = ANNOTATION_SCHEMAS_PATH / "annotation_schema.json"

# Label Studio Folder
LABEL_STUDIO_PATH = BASE_DIR / "label_studio"

LABEL_STUDIO_CONFIG = LABEL_STUDIO_PATH / "config.xml"
LABEL_STUDIO_TASKS = LABEL_STUDIO_PATH / "tasks.json"
LABEL_STUDIO_INFO = LABEL_STUDIO_PATH / "project_info.txt"

# Preprocessing Folder
PREPROCESSING_PATH = BASE_DIR / "preprocessing"

PDF_PREPROCESS_PATH = PREPROCESSING_PATH / "pdf"
JPG_PREPROCESS_PATH = PREPROCESSING_PATH / "jpg"
DWG_PREPROCESS_PATH = PREPROCESSING_PATH / "dwg"
DXF_PREPROCESS_PATH = PREPROCESSING_PATH / "dxf"

# Documentation
ANNOTATION_PIPELINE_DOC = DOCS_PATH/ "annotation_pipeline.md"

# Output
ANNOTATION_SUMMARY = OUTPUTS_PATH / "annotation_summary.csv"

# ============================================================
# MEMBER 4 - ACTIVE LEARNING LOOP
# ============================================================

FEEDBACK_PATH = BASE_DIR / "feedback"

REVIEW_QUEUE_PATH = FEEDBACK_PATH / "review_queue"
CORRECTIONS_PATH = FEEDBACK_PATH / "corrections"
TRAINING_STORE_PATH = FEEDBACK_PATH / "training_store"
FEEDBACK_LOGS_PATH = FEEDBACK_PATH / "logs"

REVIEW_QUEUE_FILE = REVIEW_QUEUE_PATH / "review_queue.json"

CORRECTIONS_FILE = CORRECTIONS_PATH / "corrections.json"

TRAINING_DATA_FILE = TRAINING_STORE_PATH / "training_data.json"

FEEDBACK_PIPELINE_DOC = DOCS_PATH / "feedback_pipeline.md"

FEEDBACK_SUMMARY = OUTPUTS_PATH / "feedback_summary.txt"