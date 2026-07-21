import fitz 
from pathlib import Path


class ImageExtractor:
    

    def __init__(self):
        pass

    def extract_images(self, pdf_path: str, output_dir: str = "output/images") -> list:
       

        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        extracted_images = []

        document = fitz.open(pdf_file)

        try:
            pdf_name = pdf_file.stem

            for page_number in range(document.page_count):

                page = document.load_page(page_number)
                images = page.get_images(full=True)

                for image_index, image in enumerate(images, start=1):

                    xref = image[0]

                    base_image = document.extract_image(xref)

                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    filename = (
                        f"{pdf_name}_page_{page_number + 1}_img_{image_index}.{image_ext}"
                    )

                    image_path = output_path / filename

                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)

                    extracted_images.append(
                        {
                            "page": page_number + 1,
                            "image_index": image_index,
                            "filename": filename,
                            "path": str(image_path),
                            "extension": image_ext,
                            "size_bytes": len(image_bytes),
                        }
                    )

        finally:
            document.close()

        return extracted_images


if __name__ == "__main__":

    extractor = ImageExtractor()

    sample_pdf = "sample.pdf"

    try:
        images = extractor.extract_images(sample_pdf)

        print(f"\nTotal Images Extracted: {len(images)}\n")

        for image in images:
            print(image)

    except Exception as e:
        print(f"Error: {e}")