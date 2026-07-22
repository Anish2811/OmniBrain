from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np


class BaseVectorDB(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def add_documents(
        self,
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ):
        pass

    @abstractmethod
    def update_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ):
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ):
        pass

    @abstractmethod
    def delete(self, ids: List[str]):
        pass

    @abstractmethod
    def close(self):
        pass


class ConfigurableVectorDB(BaseVectorDB):

    def __init__(self):
        self.documents = {}
        self.connected = False

    def connect(self):
        self.connected = True
        print("Vector database connected.")

    def add_documents(self, embeddings, metadata):
        if not self.connected:
            raise RuntimeError("Vector database is not connected.")

        for i, embedding in enumerate(embeddings):
            doc_id = f"doc_{len(self.documents) + 1}"

            self.documents[doc_id] = {
                "embedding": embedding,
                "metadata": metadata[i] if i < len(metadata) else {}
            }

        print(f"Stored {len(embeddings)} embeddings.")

    def update_documents(self, ids, embeddings, metadata):
        if not self.connected:
            raise RuntimeError("Vector database is not connected.")

        for i, doc_id in enumerate(ids):
            if doc_id in self.documents:
                self.documents[doc_id] = {
                    "embedding": embeddings[i],
                    "metadata": metadata[i] if i < len(metadata) else {}
                }

        print(f"Updated {len(ids)} documents.")

    def search(self, query_embedding, top_k=5):
        if not self.connected:
            raise RuntimeError("Vector database is not connected.")

        query = np.array(query_embedding)
        results = []

        for doc_id, doc in self.documents.items():
            embedding = np.array(doc["embedding"])

            similarity = np.dot(query, embedding) / (
                np.linalg.norm(query) * np.linalg.norm(embedding)
            )

            results.append({
                "id": doc_id,
                "score": float(similarity),
                "metadata": doc["metadata"]
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]

    def delete(self, ids):
        if not self.connected:
            raise RuntimeError("Vector database is not connected.")

        deleted_count = 0

        for doc_id in ids:
            if doc_id in self.documents:
                del self.documents[doc_id]
                deleted_count += 1

        print(f"Deleted {deleted_count} documents.")

    def close(self):
        self.connected = False
        print("Vector database connection closed.")