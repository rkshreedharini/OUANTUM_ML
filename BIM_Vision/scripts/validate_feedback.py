import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    CORRECTIONS_FILE,
    TRAINING_STORE_PATH,
    TRAINING_DATA_FILE
)
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

print("=" * 60)
print(" MEMBER 4 - FEEDBACK LOOP VALIDATION ")
print("=" * 60)

items = [
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

found = 0

for name, path in items:
    if path.exists():
        print(f"✅ {name:<30} Found")
        found += 1
    else:
        print(f"❌ {name:<30} Missing")

print("=" * 60)
print(f"Validation Completed : {found}/{len(items)} Items Found")
print("=" * 60)

if found == len(items):
    print("🎉 Member 4 setup completed successfully.")
else:
    print("⚠️ Some files/folders are missing.")