from typing import List, Dict, Any, Optional
import logging

from ingestion.embeddings import EmbeddingGenerator
from ingestion.vector_db import ConfigurableVectorDB


logger = logging.getLogger(__name__)


class DocumentRetriever:

    def __init__(
        self,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        vector_db: Optional[ConfigurableVectorDB] = None,
    ):

        self.embedding_generator = (
            embedding_generator
            if embedding_generator is not None
            else EmbeddingGenerator()
        )

        self.vector_db = (
            vector_db
            if vector_db is not None
            else ConfigurableVectorDB()
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        logger.info(
            "Retrieving documents for query with top_k=%d",
            top_k,
        )

        query_embedding = self._generate_query_embedding(query)

        try:
            self.vector_db.connect()

            results = self._search_vector_db(
                query_embedding=query_embedding,
                top_k=top_k,
                metadata_filter=metadata_filter,
            )

            logger.info(
                "Retrieved %d documents.",
                len(results),
            )

            return results

        finally:
            self.vector_db.close()

    def _generate_query_embedding(
        self,
        query: str,
    ) -> List[float]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        return self.embedding_generator.generate_embedding(
            query.strip()
        )

    def _search_vector_db(
        self,
        query_embedding: List[float],
        top_k: int,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:

        search_limit = top_k

        if metadata_filter:
            search_limit = max(top_k * 5, top_k)

        results = self.vector_db.search(
            query_embedding=query_embedding,
            top_k=search_limit,
        )

        if metadata_filter:
            results = [
                result
                for result in results
                if self._matches_metadata_filter(
                    result.get("metadata", {}),
                    metadata_filter,
                )
            ]

        return results[:top_k]

    @staticmethod
    def _matches_metadata_filter(
        metadata: Dict[str, Any],
        metadata_filter: Dict[str, Any],
    ) -> bool:

        if not metadata_filter:
            return True

        return all(
            metadata.get(key) == expected_value
            for key, expected_value in metadata_filter.items()
        )