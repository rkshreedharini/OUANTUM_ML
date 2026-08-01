import numpy as np
import matplotlib.pyplot as plt

from bim.context.fusion import FusionEngine
from bim.context.schema import BuildingContext
from bim.context.validators import ValidationEngine
from bim.context.review_queue import ReviewQueue


fusion = FusionEngine()

# -------------------------
# Sample Wall Mask
# -------------------------

mask = np.zeros((200, 200), dtype=np.uint8)

# Horizontal wall
mask[50:60, 30:170] = 255

# Vertical wall
mask[50:150, 100:110] = 255

# -------------------------
# Skeletonization
# -------------------------

skeleton = fusion.skeletonize_mask(mask)

# -------------------------
# Centerline Extraction
# -------------------------

centerlines = fusion.extract_centerlines(skeleton)

for line in centerlines:

    snapped, status = fusion.snap_to_orthogonal(line)

    print("Snapped :", status)
    print("First 10 Snapped Points :", snapped[:10])

# -------------------------
# Sample Room Polygon
# -------------------------

room_polygons = {
    "Room_1": [
        (20, 20),
        (180, 20),
        (180, 100),
        (20, 100)
    ],
}

# -------------------------
# Sample OCR Result
# -------------------------

ocr_results = [
    {
        "text": "Kitchen",
        "x": 100,
        "y": 50
    }
]

# -------------------------
# Attach OCR Labels
# -------------------------

room_labels = fusion.attach_room_labels(
    room_polygons,
    ocr_results
)

print("\nRoom Labels")
print(room_labels)

# -------------------------
# Sample Door Detection
# -------------------------

openings = [
    {
        "id": "Door_1",
        "x": 100,
        "y": 55
    }
]

opening_map = fusion.project_openings(
    centerlines,
    openings
)

print("\nOpening Mapping")
print(opening_map)

context = fusion.run(
    mask,
    room_polygons,
    ocr_results,
    openings,
    dimensions=[1000, 1200, 900],
    scalebar=1000,
    door_widths=[900, 910, 890]
)

#----------------------- 
# Validation Engine
#-----------------------
validator = ValidationEngine()

issues = validator.validate_all(context)

print("\nValidation Issues")

if len(issues) == 0:
    print("No validation errors found.")
else:
    for issue in issues:
        print(issue.description)

# -----------------------
# Review Queue
# -----------------------

review_queue = ReviewQueue()

review_items = review_queue.generate_review_queue(issues)

print("\nReview Queue")

if len(review_items) == 0:
    print("No items require manual review.")
else:
    for item in review_items:
        print(item.description)
# ---------------------
# Building Context Summary
# -----------------------
print("\nBuilding Context Created Successfully!")

print("Number of Walls :", len(context.walls))

print("Number of Rooms :", len(context.rooms))

print("Number of Dimensions :", len(context.dimensions))



# -------------------------
# Display Images (LAST)
# -------------------------

plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title("Original Wall Mask")
plt.imshow(mask, cmap="gray")

plt.subplot(1, 2, 2)
plt.title("Skeleton")
plt.imshow(skeleton, cmap="gray")

plt.show()

