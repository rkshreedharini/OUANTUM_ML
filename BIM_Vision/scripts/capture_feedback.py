import json
from pathlib import Path
import sys


# Add project root
sys.path.append(str(Path(__file__).resolve().parent.parent))


from config import (
    REVIEW_QUEUE_FILE,
    CORRECTIONS_PATH,
    CORRECTIONS_FILE
)

print("=" * 60)
print("        CAPTURE HUMAN CORRECTIONS")
print("=" * 60)

# Create corrections folder
CORRECTIONS_PATH.mkdir(parents=True, exist_ok=True)

# Check review queue
if not REVIEW_QUEUE_FILE.exists():
    print("Review Queue File Not Found!")
    exit()

# Read review queue
with open(REVIEW_QUEUE_FILE, "r", encoding="utf-8") as f:
    review_data = json.load(f)

corrections = []

for item in review_data:
    correction = {
        "element_id": item["element_id"],
        "field": item["field"],
        "old_value": item["old_value"],
        "new_value": item["new_value"],
        "reviewer_id": item["reviewer_id"]
    }

    corrections.append(correction)

# Save corrections
with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
    json.dump(corrections, f, indent=4)

print(f"Corrections Captured : {len(corrections)}")
print("Saved To :", CORRECTIONS_FILE)
print("=" * 60)