# BIM Vision - Annotation Pipeline

## Member 3: Annotation Tooling Owner

### Objective

The annotation pipeline prepares client floor plan drawings for AI model training by converting different input formats into a standardized annotation workflow.

---

## Supported Input Formats

- Scanned PDF
- Phone Photo (JPG/JPEG)
- DWG
- DXF

---

## Pipeline Workflow

Client Data

↓

Preprocessing

↓

Annotation

↓

Export Labels

↓

Training Dataset

---

## Step 1: Client Data Intake

Input drawings are collected from:

- scanned_pdf/
- phone_photos/
- dwg/
- dxf/

---

## Step 2: Preprocessing

Each file type is organized into its corresponding preprocessing folder.

- preprocessing/pdf/
- preprocessing/jpg/
- preprocessing/dwg/
- preprocessing/dxf/

---

## Step 3: Annotation

The annotation process uses Label Studio.

Annotation Labels:

- Room
- Wall
- Door
- Window
- Corner

Annotation Types:

- Polygon
- Rectangle
- Keypoint

---

## Step 4: Export

Annotated files are stored in:

annotations/exports/

These exported labels are used for machine learning model training.

---

## Folder Structure

annotations/

├── images/

├── labels/

├── exports/

└── schemas/

---

## Deliverables

- Annotation Schema
- Label Studio Configuration
- Annotation Pipeline
- Validation Script

---

## Pipeline Status

Ready for Annotation