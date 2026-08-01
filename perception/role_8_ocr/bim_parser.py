import re

ROOMS = [
    "KITCHEN",
    "BEDROOM",
    "MASTER",
    "LIVING ROOM",
    "DINING ROOM",
    "GARAGE",
    "PORCH",
    "STUDY",
    "LAUNDRY",
    "BATH",
    "BATH2",
    "HVAC"
]

def extract_bim(text):
    lines = text.upper().splitlines()

    rooms = []
    dimensions = []

    for line in lines:
        line = line.strip()

        # Detect room names
        for room in ROOMS:
            if room in line:
                rooms.append(room)

        # Detect dimensions like 12x14
        if re.match(r"\d+\s?[Xx]\s?\d+", line):
            dimensions.append(line)

    return {
        "rooms": list(set(rooms)),
        "dimensions": dimensions
    }