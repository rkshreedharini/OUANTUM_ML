from pathlib import Path

BASE_DIR = Path(__file__).parent

DATASET_DIR = Path(r"D:\DATASETS\BIM_Vision\datasets\client_data")

PDF_DIR = DATASET_DIR / "scanned_pdf"
IMAGE_DIR = DATASET_DIR / "phone_photos"
DXF_DIR = DATASET_DIR / "dxf"
DWG_DIR = DATASET_DIR / "dwg"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)