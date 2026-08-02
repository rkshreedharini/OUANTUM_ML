# BIM Vision - Data & Annotation Pipeline

## Project Overview

BIM Vision is a machine learning data preparation pipeline for building floor plan understanding. The objective of this project is to prepare high-quality datasets, collect client drawings, create annotation tools, and build an active learning feedback loop that continuously improves future model training.

This project implements the responsibilities assigned to all four members of the **Data & Annotation Pod**.

---

# Project Structure

```
BIM_Vision/
│
├── datasets/
├── preprocessing/
├── annotations/
├── label_studio/
├── feedback/
├── docs/
├── outputs/
├── scripts/
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

---

# Technologies Used

- Python
- Label Studio
- OpenCV
- NumPy
- Pandas
- DVC
- JSON
- Pathlib

---

# Member 1 - Public Dataset Lead

## Objective

Prepare public datasets required for training BIM Vision models.

## Responsibilities

- Download CubiCasa5K
- Download R2V/R3D
- Organize datasets
- Maintain dataset versions
- Prepare dataset documentation

## Folder Structure

```
datasets/

├── CubiCasa5K/
├── R2V_R3D/
```

## Deliverables

- Public datasets
- Dataset organization
- Dataset verification
- Dataset documentation

---

# Member 2 - Client Data Sourcing Lead

## Objective

Prepare real client drawings for annotation.

## Responsibilities

- Organize scanned PDFs
- Organize phone photographs
- Organize DWG drawings
- Organize DXF drawings
- Create intake metadata
- Standardize client data

## Folder Structure

```
datasets/

└── client_data/

    ├── scanned_pdf/
    ├── phone_photos/
    ├── dwg/
    ├── dxf/
    └── intake_metadata.csv
```

## Deliverables

- Client drawing repository
- Intake metadata
- Standardized data format

---

# Member 3 - Annotation Tooling Owner

## Objective

Build an annotation environment for floor plan labeling.

## Responsibilities

- Configure Label Studio
- Create annotation schema
- Build preprocessing routing
- Prepare annotation pipeline

## Folder Structure

```
annotations/

├── images/
├── labels/
├── exports/
└── schemas/
    └── annotation_schema.json

label_studio/

├── config.xml
├── tasks.json
└── project_info.txt

preprocessing/

├── pdf/
├── jpg/
├── dwg/
└── dxf/
```

## Annotation Schema

The annotation schema supports:

- Room
- Wall
- Door
- Window
- Corner

Relationships

- Wall bounds Room
- Door attached to Wall
- Window attached to Wall

## Deliverables

- Annotation schema
- Label Studio setup
- Annotation pipeline
- Validation scripts

---

# Member 4 - Active Learning Loop Engineer

## Objective

Capture reviewer corrections and prepare them for future model retraining.

## Responsibilities

- Read review queue
- Capture corrections
- Build training data store
- Create feedback pipeline
- Validate feedback loop

## Folder Structure

```
feedback/

├── review_queue/
│   └── review_queue.json

├── corrections/
│   └── corrections.json

├── training_store/
│   └── training_data.json

└── logs/
```

## Feedback Fields

Each correction contains

- element_id
- field
- old_value
- new_value
- reviewer_id

## Deliverables

- Feedback pipeline
- Correction capture
- Training data store
- Validation

---

# Scripts

## Member 1

- dataset verification

## Member 2

- client data preparation

## Member 3

- create_schema.py
- preprocess_annotation.py
- label_studio_setup.py
- annotation_pipeline.py
- validate_annotations.py

## Member 4

- capture_feedback.py
- training_data_store.py
- feedback_pipeline.py
- validate_feedback.py

---

# Project Workflow

```
Public Dataset
        │
        ▼
Client Data
        │
        ▼
Preprocessing
        │
        ▼
Annotation
        │
        ▼
Review Queue
        │
        ▼
Capture Corrections
        │
        ▼
Training Data Store
        │
        ▼
Next Model Retraining
```

---

# Running the Project

## Member 3

```
python scripts/create_schema.py

python scripts/preprocess_annotation.py

python scripts/label_studio_setup.py

python scripts/annotation_pipeline.py

python scripts/validate_annotations.py
```

## Member 4

```
python scripts/capture_feedback.py

python scripts/training_data_store.py

python scripts/feedback_pipeline.py

python scripts/validate_feedback.py
```

## Verify Entire Project

```
python main.py
```

---

# Outputs

The project generates

- Annotation Schema
- Label Studio Configuration
- Annotation Tasks
- Training Data Store
- Feedback Summary
- Validation Reports

---

# Future Improvements

- Automatic review queue integration
- Model retraining automation
- COCO export
- YOLO export
- Cloud storage integration
- Active learning dashboard

---

