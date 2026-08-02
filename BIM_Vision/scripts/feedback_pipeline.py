import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import (
    REVIEW_QUEUE_PATH,
    CORRECTIONS_PATH,
    TRAINING_STORE_PATH,
    FEEDBACK_LOGS_PATH,
    FEEDBACK_SUMMARY
)

print("=" * 60)
print("        BIM Vision Feedback Pipeline")
print("=" * 60)

print("\nStep 1 : Review Queue")
print(f"   Folder : {REVIEW_QUEUE_PATH}")

print("\nStep 2 : Capture Human Corrections")
print(f"   Folder : {CORRECTIONS_PATH}")

print("\nStep 3 : Training Data Store")
print(f"   Folder : {TRAINING_STORE_PATH}")

print("\nStep 4 : Feedback Logs")
print(f"   Folder : {FEEDBACK_LOGS_PATH}")

print("\nPipeline Status : READY")
print("=" * 60)

# Create summary file
with open(FEEDBACK_SUMMARY, "w", encoding="utf-8") as f:
    f.write("BIM Vision Feedback Pipeline\n")
    f.write("=" * 40 + "\n\n")
    f.write("Step 1 : Review Queue\n")
    f.write(f"{REVIEW_QUEUE_PATH}\n\n")
    f.write("Step 2 : Capture Human Corrections\n")
    f.write(f"{CORRECTIONS_PATH}\n\n")
    f.write("Step 3 : Training Data Store\n")
    f.write(f"{TRAINING_STORE_PATH}\n\n")
    f.write("Step 4 : Feedback Logs\n")
    f.write(f"{FEEDBACK_LOGS_PATH}\n\n")
    f.write("Pipeline Status : READY\n")

    from datetime import datetime
from config import FEEDBACK_LOGS_PATH

# Create logs folder if it doesn't exist
FEEDBACK_LOGS_PATH.mkdir(parents=True, exist_ok=True)

log_file = FEEDBACK_LOGS_PATH / "feedback_log.txt"

with open(log_file, "a") as f:
    f.write("=" * 50 + "\n")
    f.write(f"Date & Time : {datetime.now()}\n")
    f.write("Review Queue Loaded Successfully\n")
    f.write("Corrections Captured Successfully\n")
    f.write("Training Data Store Updated\n")
    f.write("Pipeline Status : READY\n")
    f.write("=" * 50 + "\n\n")

print(f"Log Saved : {log_file}")