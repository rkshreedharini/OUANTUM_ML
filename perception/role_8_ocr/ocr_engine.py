import easyocr
import cv2
import numpy as np

# Initialize EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

def enhance_blueprint(img):
    """
    Applies adaptive thresholding and contrast enhancement
    to make faint blueprint text stand out clearly.
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # 1. Upscale if image is low resolution
    h, w = gray.shape[:2]
    if max(h, w) < 2500:
        scale = 2500.0 / max(h, w)
        gray = cv2.resize(gray, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 2. Adaptive contrast boost (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 3. Light sharpening
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    return sharpened


def extract_text(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return ""

    enhanced_img = enhance_blueprint(img)
    all_extracted_text = []

    # Run EasyOCR across 4 angles to collect both horizontal and vertical dimension text
    for angle in [0, 90, 180, 270]:
        if angle == 0:
            current_img = enhanced_img
        elif angle == 90:
            current_img = cv2.rotate(enhanced_img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            current_img = cv2.rotate(enhanced_img, cv2.ROTATE_180)
        elif angle == 270:
            current_img = cv2.rotate(enhanced_img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        try:
            # Low text_threshold captures faint dimension numbers
            results = reader.readtext(
                current_img, 
                detail=0, 
                paragraph=False,
                text_threshold=0.3, 
                low_text=0.3
            )
            all_extracted_text.extend(results)
        except Exception:
            continue

    # Combine all detected strings across all orientations
    combined_text = "\n".join(all_extracted_text)
    return combined_text