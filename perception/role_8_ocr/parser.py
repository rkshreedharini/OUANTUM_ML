import re

ROOMS = [
    # Full Names
    "BEDROOM 2", "BEDROOM 3", "BEDROOM 4", "BEDROOM 5", "BEDROOM", 
    "MASTER BEDROOM", "MASTER", "GUEST ROOM", "PRIMARY SUITE", 
    "WET KITCHEN", "DRY KITCHEN", "KITCHEN", "GREAT ROOM", "LIVING ROOM", "LIVING", 
    "DINING ROOM", "DINING", "FAMILY ROOM", "TWO CAR GARAGE", "GARAGE", 
    "MSTR BATH", "HALL BATH", "1/2 BATH", "BATHROOM", "BATH 1", "BATH 2", "BATH 3", "BATH 4", "BATH 5", "BATH", 
    "COVERED PORCH", "FRONT PORCH", "REAR PORCH", "PORCH", "WOOD DECK", "DECK", "PATIO", "BALCONY", 
    "HOME OFFICE", "OFFICE", "STUDY", "LAUNDRY", "UTILITY", "STORAGE", "RUMPUS", 
    "FOYER", "ENTRY", "ENTRANCE", "PANTRY", "CLOSET", "WIC", "DRESSING", "INTERNAL GARDEN",
    
    # Abbreviated Blueprint Labels
    "MBR", "GRT.RM", "GRT RM", "DIN", "KIT", "STOR", "B."
]


def extract_rooms(text):
    text = text.upper()
    found = []

    # Sort ROOMS by length descending so longer phrases (e.g. DINING ROOM) match before DINING or DIN
    sorted_rooms = sorted(ROOMS, key=len, reverse=True)

    for room in sorted_rooms:
        if room in text:
            cleaned_room = room.replace("VAUNDRY", "LAUNDRY").replace("STUDX", "STUDY")
            
            # Prevents adding substrings if a longer match already exists in found
            if not any(cleaned_room in existing or existing in cleaned_room for existing in found):
                found.append(cleaned_room)

    return found


def extract_dimensions(text):
    text = text.upper()

    # Clean OCR noise
    text = text.replace("O", "0").replace("×", "X").replace("*", "X")

    # Matches: 12X14, 16'6"X14'0", 13.12X9.84, 16-6 X 14-0
    pattern = r"\b(\d{1,2}(?:\.\d+)?)\s*['′]?\s*(?:\d+[\"″])?\s*[-X\s]\s*(\d{1,2}(?:\.\d+)?)\s*['′]?"

    matches = re.findall(pattern, text)
    dimensions = []

    for w, h in matches:
        w_val = float(w)
        h_val = float(h)

        # 1. Realistic room size bounds (in feet/meters)
        if w_val < 5 or h_val < 5 or w_val > 35 or h_val > 35:
            continue

        # 2. Aspect ratio filter: ignores narrow noise strips like 4x43 or 3x51
        aspect_ratio = max(w_val, h_val) / min(w_val, h_val)
        if aspect_ratio > 3.0:
            continue

        item = {
            "width": int(round(w_val)),
            "height": int(round(h_val)),
            "unit": "ft"
        }

        if item not in dimensions:
            dimensions.append(item)

    return dimensions


def detect_scale(text):
    text = text.upper()

    patterns = [
        r"SCALE\s*[:\-]?\s*([^\n]+)",
        r"(\d+\s*:\s*\d+)",
        r'(\d+/\d+"\s*=\s*1[\'"]?)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(1).strip()

    return "Unknown"