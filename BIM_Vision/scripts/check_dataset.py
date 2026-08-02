from pathlib import Path

# Dataset Path
DATASET_PATH = Path("E:\BIM_Vision\datasets\CubiCasa5K\cubicasa5k\high_quality")

# Required files
required_files = [
    "F1_original.png",
    "F1_scaled.png",
    "model.svg"
]

total_folders = 0
complete_folders = 0
incomplete_folders = 0

print("=" * 60)
print("Checking CubiCasa5K Dataset...")
print("=" * 60)

for folder in DATASET_PATH.iterdir():

    if folder.is_dir():

        total_folders += 1
        missing = []

        for file in required_files:

            if not (folder / file).exists():
                missing.append(file)

        if len(missing) == 0:
            complete_folders += 1

        else:
            incomplete_folders += 1
            print(f"\nFolder : {folder.name}")
            print("Missing :", ", ".join(missing))

print("\n" + "=" * 60)
print("Dataset Summary")
print("=" * 60)

print(f"Total Building Folders : {total_folders}")
print(f"Complete Folders      : {complete_folders}")
print(f"Incomplete Folders    : {incomplete_folders}")

if incomplete_folders == 0:
    print("\n✅ Dataset Verification Successful")
else:
    print("\n⚠ Dataset Contains Missing Files")