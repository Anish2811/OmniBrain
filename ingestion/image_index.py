from typing import Any, Dict, List
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from ingestion.embeddings import EmbeddingGenerator


class ImageIndex:

    COLLECTION_NAME = "omnibrain_images"
    VECTOR_SIZE = 384

    def __init__(
        self,
        storage_path: str = "qdrant_data",
        embedding_generator: EmbeddingGenerator | None = None,
    ):
        self.storage_path = storage_path
        self.client = None

        self.embedding_generator = (
            embedding_generator
            if embedding_generator is not None
            else EmbeddingGenerator()
        )

    def connect(self) -> None:
        if self.client is not None:
            return

        self.client = QdrantClient(
            path=self.storage_path
        )

    def _ensure_collection(self) -> None:
        if self.client is None:
            raise RuntimeError(
                "Image index is not connected."
            )

        collections = self.client.get_collections()

        exists = any(
            collection.name == self.COLLECTION_NAME
            for collection in collections.collections
        )

        if not exists:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    def add_images(
        self,
        images: List[Dict[str, Any]],
    ) -> List[str]:

        if not images:
            return []

        self.connect()
        self._ensure_collection()

        ocr_texts = [
            image.get(
                "ocr_text",
                "",
            ).strip()
            for image in images
        ]

        valid_images = []
        valid_texts = []

        for image, ocr_text in zip(
            images,
            ocr_texts,
        ):
            if not ocr_text:
                continue

            valid_images.append(image)
            valid_texts.append(ocr_text)

        if not valid_images:
            return []

        embeddings = (
            self.embedding_generator.generate_embeddings(
                valid_texts
            )
        )

        points = []
        ids = []

        for image, ocr_text, embedding in zip(
            valid_images,
            valid_texts,
            embeddings,
        ):

            point_id = str(uuid4())

            metadata = {
                "document": image.get(
                    "document",
                    "",
                ),
                "document_path": image.get(
                    "document_path",
                    "",
                ),
                "document_type": "image",
                "page": image.get(
                    "page",
                ),
                "image_index": image.get(
                    "image_index",
                ),
                "filename": image.get(
                    "filename",
                    "",
                ),
                "path": image.get(
                    "path",
                    "",
                ),
                "extension": image.get(
                    "extension",
                    "",
                ),
                "size_bytes": image.get(
                    "size_bytes",
                    0,
                ),
                "ocr_text": ocr_text,
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=metadata,
                )
            )

            ids.append(point_id)

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

        return ids

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:

        if not query or not query.strip():
            raise ValueError(
                "Image search query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        self.connect()
        self._ensure_collection()

        query_embedding = (
            self.embedding_generator.generate_embedding(
                query.strip()
            )
        )

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
        )

        return [
            {
                "id": str(point.id),
                "score": float(point.score),
                "metadata": point.payload or {},
            }
            for point in results.points
        ]

    def count(self) -> int:
        self.connect()
        self._ensure_collection()

        result = self.client.count(
            collection_name=self.COLLECTION_NAME,
        )

        return result.count

    def close(self) -> None:
        self.client = None