from pathlib import Path

# Dataset path
DATASET_PATH = Path("E:\BIM_Vision\datasets\CubiCasa5K\cubicasa5k\high_quality")

total_buildings = 0
original_images = 0
scaled_images = 0
svg_files = 0
missing_files = 0

required_files = [
    "F1_original.png",
    "F1_scaled.png",
    "model.svg"
]

for folder in DATASET_PATH.iterdir():

    if folder.is_dir():

        total_buildings += 1

        for file in required_files:

            file_path = folder / file

            if file_path.exists():

                if file == "F1_original.png":
                    original_images += 1

                elif file == "F1_scaled.png":
                    scaled_images += 1

                elif file == "model.svg":
                    svg_files += 1

            else:
                missing_files += 1

print("=" * 50)
print("        CubiCasa5K Dataset Summary")
print("=" * 50)

print(f"Total Building Folders : {total_buildings}")
print(f"Original Images        : {original_images}")
print(f"Scaled Images          : {scaled_images}")
print(f"SVG Annotation Files   : {svg_files}")
print(f"Missing Files          : {missing_files}")

print("=" * 50)

if missing_files == 0:
    print("Status : ✅ Dataset is Complete")
else:
    print("Status : ⚠ Dataset is Incomplete")

print("=" * 50)