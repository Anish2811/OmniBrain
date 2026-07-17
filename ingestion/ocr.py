from pathlib import Path
from PIL import Image
import pytesseract


class OCRProcessor:
    """
    OCR engine for OmniBrain.

    Responsible for extracting text from scanned
    documents and images using Tesseract OCR.
    """

    def __init__(self):
        pass

    def extract_text(self, image_path: str) -> str:
        """
        Extract text from an image.
        """

        image = Image.open(image_path)

        text = pytesseract.image_to_string(image)

        return text


if __name__ == "__main__":

    ocr = OCRProcessor()

    sample = "sample.png"

    if Path(sample).exists():
        print(ocr.extract_text(sample))
    else:
        print("Sample image not found.")