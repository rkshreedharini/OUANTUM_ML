import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
    PROJECT_NAME,
    CUBICASA5K_HIGH_QUALITY,
    CUBICASA5K_COLORFUL,
    R2V_PATH,
)

def check_folder(name, path):
    if path.exists():
        print(f"✅ {name} : Found")
    else:
        print(f"❌ {name} : Not Found")

def main():
    print("=" * 60)
    print(f"{PROJECT_NAME:^60}")
    print("=" * 60)

    print("\nChecking CubiCasa5K Dataset...\n")

    check_folder("High Quality", CUBICASA5K_HIGH_QUALITY)
    check_folder("Colorful", CUBICASA5K_COLORFUL)

    print("\nChecking R2V Dataset...\n")

    image_folder = R2V_PATH / "vector_graphics_floorplans" / "floorplan_image"
    prediction_folder = R2V_PATH / "vector_graphics_floorplans" / "representation_prediction"

    check_folder("floorplan_image", image_folder)
    check_folder("representation_prediction", prediction_folder)

    print("\n" + "=" * 60)
    print("Dataset Verification Completed Successfully")
    print("=" * 60)

if __name__ == "__main__":
    main()