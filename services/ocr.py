"""Screenshot OCR utilities."""
from pathlib import Path


def extract_text(path: Path) -> str:
    """Extract readable text using OpenCV preprocessing and Tesseract."""
    import cv2
    import pytesseract
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError("Unable to read image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return pytesseract.image_to_string(gray)
