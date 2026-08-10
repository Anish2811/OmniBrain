from abc import ABC, abstractmethod
from typing import List, Dict, Any
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)


class BaseVectorDB(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def add_documents(
        self,
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]],
    ):
        pass

    @abstractmethod
    def update_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]],
    ):
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ):
        pass

    @abstractmethod
    def delete(self, ids: List[str]):
        pass

    @abstractmethod
    def close(self):
        pass


class ConfigurableVectorDB(BaseVectorDB):

    def __init__(
        self,
        collection_name: str = "omnibrain_docs",
        storage_path: str = "qdrant_data",
    ):
        self.collection_name = collection_name
        self.storage_path = storage_path

        self.client = None
        self.connected = False

    def connect(self):
        if self.connected:
            return

        self.client = QdrantClient(
            path=self.storage_path
        )

        self.connected = True

        print(
            f"Qdrant connected: {self.collection_name}"
        )

    def _ensure_collection(self, vector_size: int):
        if self.client is None:
            raise RuntimeError(
                "Qdrant client is not connected."
            )

        collections = self.client.get_collections()

        exists = any(
            collection.name == self.collection_name
            for collection in collections.collections
        )

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

            print(
                f"Created Qdrant collection: "
                f"{self.collection_name}"
            )

    def add_documents(
        self,
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]],
    ):
        if not self.connected:
            raise RuntimeError(
                "Vector database is not connected."
            )

        if not embeddings:
            return

        self._ensure_collection(
            vector_size=len(embeddings[0])
        )

        points = []

        for i, embedding in enumerate(embeddings):

            payload = (
                metadata[i]
                if i < len(metadata)
                else {}
            )

            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        print(
            f"Stored {len(points)} embeddings in Qdrant."
        )

    def update_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]],
    ):
        if not self.connected:
            raise RuntimeError(
                "Vector database is not connected."
            )

        if not embeddings:
            return

        if len(ids) != len(embeddings):
            raise ValueError(
                "Number of IDs must match number of embeddings."
            )

        self._ensure_collection(
            vector_size=len(embeddings[0])
        )

        points = []

        for i, doc_id in enumerate(ids):

            payload = (
                metadata[i]
                if i < len(metadata)
                else {}
            )

            points.append(
                PointStruct(
                    id=str(doc_id),
                    vector=embeddings[i],
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        print(
            f"Updated {len(points)} documents."
        )

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ):
        if not self.connected:
            raise RuntimeError(
                "Vector database is not connected."
            )

        if not query_embedding:
            return []

        self._ensure_collection(
            vector_size=len(query_embedding)
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
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

    def delete(self, ids: List[str]):
        if not self.connected:
            raise RuntimeError(
                "Vector database is not connected."
            )

        if not ids:
            return

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids,
        )

        print(
            f"Deleted {len(ids)} documents."
        )

    def close(self):
        self.client = None
        self.connected = False

        print("Qdrant connection closed.")