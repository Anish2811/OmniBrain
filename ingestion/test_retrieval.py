from ingestion.retrieval import DocumentRetriever
from ingestion.vector_db import ConfigurableVectorDB


class TestEmbeddingGenerator:

    def generate_embedding(self, text):
        text = text.lower()

        if "python" in text:
            return [1.0, 0.0, 0.0]

        if "financial" in text:
            return [0.0, 1.0, 0.0]

        return [0.0, 0.0, 1.0]


def create_test_vector_db():

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

    return vector_db


def test_basic_retrieval():
    
    vector_db = create_test_vector_db()

    retriever = DocumentRetriever(
        embedding_generator=TestEmbeddingGenerator(),
        vector_db=vector_db,
    )

    results = retriever.retrieve(
        query="Python programming",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["metadata"]["document_type"] == "technical"

    print("PASS: basic retrieval")


def test_metadata_filter():
    
    vector_db = create_test_vector_db()

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

    assert len(results) == 1
    assert results[0]["metadata"]["document_type"] == "technical"

    print("PASS: metadata filtering")


def test_empty_query():

    retriever = DocumentRetriever(
        embedding_generator=TestEmbeddingGenerator(),
        vector_db=ConfigurableVectorDB(),
    )

    try:
        retriever.retrieve("")
    except ValueError as exc:
        assert str(exc) == "Query cannot be empty."
        print("PASS: empty query validation")
    else:
        raise AssertionError(
            "Expected ValueError for empty query"
        )


def test_invalid_top_k():
   
    retriever = DocumentRetriever(
        embedding_generator=TestEmbeddingGenerator(),
        vector_db=ConfigurableVectorDB(),
    )

    try:
        retriever.retrieve(
            query="Python",
            top_k=0,
        )
    except ValueError as exc:
        assert str(exc) == "top_k must be greater than 0."
        print("PASS: top_k validation")
    else:
        raise AssertionError(
            "Expected ValueError for top_k=0"
        )


def main():
    print("=" * 60)
    print("OmniBrain Retrieval Tests")
    print("=" * 60)

    test_basic_retrieval()
    test_metadata_filter()
    test_empty_query()
    test_invalid_top_k()

    print("=" * 60)
    print("All retrieval tests passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()