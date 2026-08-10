import logging
from typing import List, Optional

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingGenerator:

    DEFAULT_MODEL = "all-MiniLM-L6-v2"

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self.model: Optional[SentenceTransformer] = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(model_name={self.model_name!r})"
        )

    def configure(self, model_name: str) -> None:
        if not model_name or not model_name.strip():
            raise ValueError("Model name cannot be empty.")

        self.model_name = model_name.strip()
        self.model = None

        logger.info(
            "Embedding model configured: %s",
            self.model_name,
        )

    def load_model(self) -> None:
        logger.info(
            "Loading embedding model: %s",
            self.model_name,
        )

        self.model = SentenceTransformer(self.model_name)

        logger.info(
            "Embedding model loaded successfully."
        )

    def _ensure_model(self) -> None:
        if self.model is None:
            self.load_model()

    def generate_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        self._ensure_model()

        embedding = self.model.encode(
            text.strip(),
            convert_to_numpy=True,
        )

        return embedding.tolist()

    def generate_embeddings(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        if not texts:
            raise ValueError("Input text list cannot be empty.")

        cleaned_texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not cleaned_texts:
            raise ValueError(
                "Input text list contains no valid text."
            )

        self._ensure_model()

        embeddings = self.model.encode(
            cleaned_texts,
            convert_to_numpy=True,
        )

        return embeddings.tolist()