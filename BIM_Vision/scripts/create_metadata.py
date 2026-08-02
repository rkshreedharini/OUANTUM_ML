import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import csv
from config import METADATA_FILE

header = [
    "File_Name",
    "File_Type",
    "Source",
    "Received_Date",
    "Status"
]

if not METADATA_FILE.exists():

    with open(METADATA_FILE, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow(header)

    print("Metadata file created successfully!")

else:

    print("Metadata file already exists.")

print("Location:", METADATA_FILE)