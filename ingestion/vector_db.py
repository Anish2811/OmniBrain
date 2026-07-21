from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseVectorDB(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def add_documents(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]):
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5):
        pass

    @abstractmethod
    def delete(self, ids: List[str]):
        pass

    @abstractmethod
    def close(self):
        pass


class ConfigurableVectorDB(BaseVectorDB):
    
    def connect(self):
        print("Vector database connection placeholder.")

    def add_documents(self, embeddings, metadata):
        print(f"Placeholder: storing {len(embeddings)} embeddings.")

    def search(self, query_embedding, top_k=5):
        print(f"Placeholder: retrieving top {top_k} matches.")
        return []

    def delete(self, ids):
        print(f"Placeholder: deleting {len(ids)} documents.")

    def close(self):
        print("Closing vector database placeholder.")