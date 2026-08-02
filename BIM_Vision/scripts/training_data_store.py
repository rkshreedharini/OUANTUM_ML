import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import json

from config import (
    CORRECTIONS_FILE,
    TRAINING_STORE_PATH,
    TRAINING_DATA_FILE
)

print("=" * 60)
print("         TRAINING DATA STORE")
print("=" * 60)

# Create training store folder
TRAINING_STORE_PATH.mkdir(parents=True, exist_ok=True)

# Check corrections file
if not CORRECTIONS_FILE.exists():
    print("Corrections File Not Found!")
    exit()

# Read corrections
with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
    corrections = json.load(f)

training_data = []

for item in corrections:
    training_record = {
        "element_id": item["element_id"],
        "field": item["field"],
        "corrected_value": item["new_value"],
        "reviewer_id": item["reviewer_id"]
    }

    training_data.append(training_record)

# Save training data
with open(TRAINING_DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(training_data, f, indent=4)

print(f"Training Records : {len(training_data)}")
print("Saved To :", TRAINING_DATA_FILE)
print("=" * 60)