from fastapi import APIRouter, HTTPException

from backend.app.api.schemas import QueryRequest
from backend.app.api.schemas import QueryResponse
from backend.app.api.schemas import SourceCitation

from ingestion.retrieval import DocumentRetriever


router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):

    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    try:
        retriever = DocumentRetriever()

        results = retriever.retrieve(
            request.query.strip(),
            top_k=request.top_k,
        )

        citations = []

        for result in results:
            metadata = result.get("metadata", {})

            citations.append(
                SourceCitation(
                    source_type=metadata.get(
                        "document_type",
                        "text",
                    ),
                    content_snippet=metadata.get(
                        "text",
                        "",
                    )[:500],
                    page_number=metadata.get(
                        "page_number"
                    ),
                    score=result.get("score"),
                )
            )

        if not results:
            return QueryResponse(
                answer=(
                    "I could not find relevant information "
                    "in the uploaded documents."
                ),
                citations=[],
                agent_trace=[
                    "retrieval",
                    "no_results",
                ],
            )

        context_parts = []

        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})
            text = metadata.get("text", "").strip()

            if text:
                context_parts.append(
                    f"Source {index}:\n{text}"
                )

        context = "\n\n".join(context_parts)

        answer = (
            "Based on the retrieved document context:\n\n"
            f"{context}"
        )

        return QueryResponse(
            answer=answer,
            citations=citations,
            agent_trace=[
                "retrieval",
                "qdrant",
            ],
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG retrieval failed: {exc}",
        )