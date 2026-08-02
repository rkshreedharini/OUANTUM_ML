import json
from pathlib import Path
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
    LABEL_STUDIO_PATH,
    LABEL_STUDIO_CONFIG,
    LABEL_STUDIO_TASKS,
    LABEL_STUDIO_INFO,
    ANNOTATION_IMAGES_PATH,
)

# Create Label Studio folder
LABEL_STUDIO_PATH.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Create config.xml
# -----------------------------
config_xml = """<View>
    <Image name="image" value="$image"/>
    <PolygonLabels name="label" toName="image">
        <Label value="Room"/>
        <Label value="Wall"/>
        <Label value="Door"/>
        <Label value="Window"/>
    </PolygonLabels>
</View>
"""

with open(LABEL_STUDIO_CONFIG, "w", encoding="utf-8") as f:
    f.write(config_xml)

# -----------------------------
# Create tasks.json automatically
# -----------------------------
tasks = []

image_extensions = [".jpg", ".jpeg", ".png"]

image_files = sorted(
    [
        img
        for img in ANNOTATION_IMAGES_PATH.iterdir()
        if img.suffix.lower() in image_extensions
    ]
)

for i, image in enumerate(image_files, start=1):
    tasks.append(
        {
            "id": i,
            "data": {
                "image": f"annotations/images/{image.name}"
            }
        }
    )

with open(LABEL_STUDIO_TASKS, "w", encoding="utf-8") as f:
    json.dump(tasks, f, indent=4)

# -----------------------------
# Create project_info.txt
# -----------------------------
with open(LABEL_STUDIO_INFO, "w", encoding="utf-8") as f:
    f.write("Label Studio Project\n")
    f.write("====================\n\n")
    f.write("Project Name : BIM Vision Annotation\n")
    f.write("Labels       : Room, Wall, Door, Window\n")
    f.write(f"Images Found : {len(tasks)}\n")
    f.write("Status       : Ready for Annotation\n")

print("=" * 50)
print("Label Studio Setup Completed")
print("=" * 50)
print("Config File :", LABEL_STUDIO_CONFIG)
print("Tasks File  :", LABEL_STUDIO_TASKS)
print("Project Info:", LABEL_STUDIO_INFO)
print(f"Images Added: {len(tasks)}")