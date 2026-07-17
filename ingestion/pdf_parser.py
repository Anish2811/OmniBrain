import fitz  # PyMuPDF
from pathlib import Path


class PDFParser:
    """
    PDF document parser for the OmniBrain ingestion pipeline.
    Responsible for loading PDF documents and extracting text.
    """

    def __init__(self):
        pass

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from all pages of a PDF.
        """

        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")

        document = fitz.open(pdf_file)

        extracted_text = ""

        for page in document:
            extracted_text += page.get_text()

        document.close()

        return extracted_text

    def get_metadata(self, pdf_path: str) -> dict:
        """
        Extract basic PDF metadata.
        """

        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")

        document = fitz.open(pdf_file)

        metadata = document.metadata
        metadata["page_count"] = document.page_count

        document.close()

        return metadata


if __name__ == "__main__":

    parser = PDFParser()

    sample_pdf = "sample.pdf"

    try:
        print("----- PDF Metadata -----")
        print(parser.get_metadata(sample_pdf))

        print("\n----- Extracted Text -----")
        print(parser.extract_text(sample_pdf))

    except Exception as e:
        print(f"Error: {e}")