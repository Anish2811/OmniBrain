import logging

from pdf_parser import PDFParser
from table_extractor import TableExtractor
from image_extractor import ImageExtractor
from ocr import OCRProcessor
from chunking import TextChunker
from embeddings import EmbeddingGenerator
from vector_db import ConfigurableVectorDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentIngestionPipeline:
    

    def __init__(self):
        self.pdf_parser = PDFParser()
        self.table_extractor = TableExtractor()
        self.image_extractor = ImageExtractor()
        self.ocr = OCRProcessor()
        self.chunker = TextChunker()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = ConfigurableVectorDB()

    def process_document(self, document_path: str):
        

        logger.info(f"Processing document: {document_path}")

        text = self.pdf_parser.extract_text(document_path)

        tables = self.table_extractor.extract_tables(document_path)

        images = self.image_extractor.extract_images(document_path)

        ocr_text = self.ocr.extract_text(document_path)

        chunks = self.chunker.chunk_text(text)

        embeddings = self.embedding_generator.generate_embeddings(chunks)

        self.vector_db.connect()

        self.vector_db.add_documents(
            embeddings=[],
            metadata=[]
        )

        self.vector_db.close()

        logger.info("Document processed successfully.")

        return {
            "parsed_document": parsed_document,
            "tables": tables,
            "images": images,
            "text": text,
            "chunks": chunks,
            "embeddings": embeddings,
        }