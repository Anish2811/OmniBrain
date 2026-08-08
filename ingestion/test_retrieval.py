from ingestion.retrieval import DocumentRetriever
from ingestion.vector_db import ConfigurableVectorDB

class TestEmbeddingGenerator:

    def generate_embedding(self, text):
        if "python" in text.lower():
            return [1.0, 0.0, 0.0]

        return [0.0, 1.0, 0.0]


def main():
    vector_db = ConfigurableVectorDB()

    vector_db.connect()

    vector_db.add_documents(
        embeddings=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        metadata=[
            {
                "text": "Python programming document",
                "document_type": "technical",
            },
            {
                "text": "Financial report document",
                "document_type": "financial",
            },
        ],
    )

    vector_db.close()

    retriever = DocumentRetriever(
        embedding_generator=TestEmbeddingGenerator(),
        vector_db=vector_db,
    )

    results = retriever.retrieve(
    query="Python programming",
    top_k=5,
    metadata_filter={
        "document_type": "technical"
    },
)

    print("\nRetrieval Results:")
    print(results)


if __name__ == "__main__":
    main()