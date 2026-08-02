from pathlib import Path

# Dataset Path
DATASET_PATH = Path("E:\BIM_Vision\datasets\CubiCasa5K\cubicasa5k\high_quality")

# Count building folders
building_count = 0

for folder in DATASET_PATH.iterdir():
    if folder.is_dir():
        building_count += 1

print("=" * 40)
print("CubiCasa5K Dataset Summary")
print("=" * 40)
print(f"Total Building Folders : {building_count}")
print("=" * 40)