import csv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import (
    SCANNED_PDF_PATH,
    PHONE_PHOTOS_PATH,
    DWG_PATH,
    DXF_PATH,
    INTAKE_SUMMARY
)

folders = {
    "Scanned PDF": SCANNED_PDF_PATH,
    "Phone Photos": PHONE_PHOTOS_PATH,
    "DWG": DWG_PATH,
    "DXF": DXF_PATH
}

with open(INTAKE_SUMMARY, "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow(["Folder", "Number_of_Files"])

    total = 0

    for name, folder in folders.items():

        count = len(list(folder.glob("*"))) if folder.exists() else 0

        writer.writerow([name, count])

        total += count

    writer.writerow(["Total", total])

print("Summary created successfully!")
print("Location:", INTAKE_SUMMARY)