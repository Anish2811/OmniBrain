import logging
from pathlib import Path
from typing import Any, Dict

from ingestion.pdf_parser import PDFParser
from ingestion.table_extractor import TableExtractor
from ingestion.image_extractor import ImageExtractor
from ingestion.ocr import OCRProcessor
from ingestion.chunking import TextChunker
from ingestion.embeddings import EmbeddingGenerator
from ingestion.vector_db import ConfigurableVectorDB


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

    def process_document(self, document_path: str) -> Dict[str, Any]:


        document = Path(document_path)

        if not document.exists():
            raise FileNotFoundError(
                f"Document not found: {document_path}"
            )

        logger.info(
            "Processing document: %s",
            document_path
        )

       
        metadata = self.pdf_parser.get_metadata(
            document_path
        )

       
        text = self.pdf_parser.extract_text(
            document_path
        )

        logger.info(
            "Extracted %d characters of text.",
            len(text)
        )

       
        tables = []

        if self.table_extractor.backend is not None:
            tables = self.table_extractor.extract_tables(
                document_path
            )
        else:
            logger.info(
                "No table extraction backend configured. "
                "Skipping table extraction."
            )

        images = self.image_extractor.extract_images(
            document_path
        )

        logger.info(
            "Extracted %d images.",
            len(images)
        )

        
        ocr_results = []

        for image in images:
            image_path = image["path"]

            try:
                extracted_text = self.ocr.extract_text(
                    image_path
                )

                ocr_results.append(
                    {
                        "page": image["page"],
                        "image_index": image["image_index"],
                        "image_path": image_path,
                        "text": extracted_text,
                    }
                )

            except Exception as exc:
                logger.warning(
                    "OCR failed for image %s: %s",
                    image_path,
                    exc,
                )

        ocr_text = "\n".join(
            result["text"]
            for result in ocr_results
            if result["text"].strip()
        )

        
        chunks = self.chunker.chunk_text(text)

        logger.info(
            "Created %d text chunks.",
            len(chunks)
        )

    
        chunk_texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.embedding_generator.generate_embeddings(
            chunk_texts
        )

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings does not match "
                "number of text chunks."
            )


        vector_metadata = []

        for chunk in chunks:
            vector_metadata.append(
                {
                    "document": document.name,
                    "document_path": str(document),
                    "document_type": "pdf",
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "word_start": chunk["word_start"],
                    "word_end": chunk["word_end"],
                }
            )

    
        self.vector_db.connect()

        try:
            self.vector_db.add_documents(
                embeddings=embeddings,
                metadata=vector_metadata,
            )
        finally:
            self.vector_db.close()

        logger.info(
            "Document processed successfully: %s",
            document_path
        )

        return {
            "document_path": str(document),
            "metadata": metadata,
            "text": text,
            "ocr_text": ocr_text,
            "ocr_results": ocr_results,
            "tables": tables,
            "images": images,
            "chunks": chunks,
            "embeddings": embeddings,
            "vector_metadata": vector_metadata,
        }