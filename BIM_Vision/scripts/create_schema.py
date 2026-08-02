import sys
import json
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
    ANNOTATION_SCHEMAS_PATH,
    ANNOTATION_SCHEMA_FILE
)

# Create schemas folder if it doesn't exist
ANNOTATION_SCHEMAS_PATH.mkdir(parents=True, exist_ok=True)

# Annotation schema
schema = {
    "project": "BIM Vision Annotation",
    "version": "1.0",
    "labels": [
        {
            "name": "Room",
            "type": "Polygon"
        },
        {
            "name": "Wall",
            "type": "Polygon"
        },
        {
            "name": "Door",
            "type": "Rectangle"
        },
        {
            "name": "Window",
            "type": "Rectangle"
        },
        {
            "name": "Corner",
            "type": "Keypoint"
        }
    ],
    "relationships": [
        {
            "from": "Wall",
            "to": "Room",
            "relation": "bounds"
        },
        {
            "from": "Door",
            "to": "Wall",
            "relation": "attached_to"
        },
        {
            "from": "Window",
            "to": "Wall",
            "relation": "attached_to"
        }
    ]
}

# Save schema
with open(ANNOTATION_SCHEMA_FILE, "w") as file:
    json.dump(schema, file, indent=4)

print("=" * 50)
print(" Annotation Schema Created Successfully")
print("=" * 50)
print(f"Location : {ANNOTATION_SCHEMA_FILE}")