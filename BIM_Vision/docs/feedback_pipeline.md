# BIM Vision Feedback Pipeline

## Objective

Capture reviewer corrections from the review queue and prepare them for the next model retraining cycle.

---

## Workflow

Review Queue
↓

Capture Human Corrections
↓

Training Data Store
↓

Ready for Retraining

---

## Correction Fields

Each correction contains:

- element_id
- field
- old_value
- new_value
- reviewer_id

---

## Folder Structure

feedback/
├── review_queue/
├── corrections/
├── training_store/
└── logs/

---

## Output

The processed corrections are stored in the training data store and can be used during the next model retraining cycle.

---

## Pipeline Status

READY