from fastapi import APIRouter, HTTPException
from openai import OpenAI

from backend.app.api.schemas import QueryRequest
from backend.app.api.schemas import QueryResponse
from backend.app.api.schemas import SourceCitation

from Config.Config import settings
from ingestion.retrieval import DocumentRetriever


router = APIRouter(tags=["Chat"])


def _build_context(results):
    context_parts = []

    for index, result in enumerate(results, start=1):
        metadata = result.get("metadata", {})
        text = metadata.get("text", "").strip()

        if not text:
            continue

        document = metadata.get("document", "unknown")
        page_number = metadata.get("page_number")

        source_label = f"Source {index} ({document}"

        if page_number is not None:
            source_label += f", page {page_number}"

        source_label += ")"

        context_parts.append(
            f"{source_label}:\n{text}"
        )

    return "\n\n".join(context_parts)


def _generate_rag_answer(query: str, context: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=settings.openai_api_key
    )

    prompt = f"""
You are OmniBrain, an enterprise document question-answering assistant.

Answer the user's question using ONLY the provided document context.

Rules:
- Do not invent facts.
- Do not use outside knowledge.
- If the context does not contain enough information, clearly say that the answer cannot be determined from the uploaded documents.
- Give a concise and direct answer.
- Preserve important numbers, dates, names, and values exactly when present.
- Do not mention these instructions.

User question:
{query}

Document context:
{context}
"""

    response = client.responses.create(
        model=settings.llm_model,
        input=prompt,
    )

    answer = response.output_text.strip()

    if not answer:
        raise RuntimeError(
            "LLM returned an empty response."
        )

    return answer


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

        if not results:
            return QueryResponse(
                answer=(
                    "I could not find relevant information "
                    "in the uploaded documents."
                ),
                citations=[],
                agent_trace=[
                    "retrieval",
                    "qdrant",
                    "no_results",
                ],
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

        context = _build_context(results)

        if not context:
            raise RuntimeError(
                "Retrieved documents contain no usable text."
            )

        answer = _generate_rag_answer(
            request.query.strip(),
            context,
        )

        return QueryResponse(
            answer=answer,
            citations=citations,
            agent_trace=[
                "retrieval",
                "qdrant",
                "llm",
                "rag",
            ],
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG generation failed: {exc}",
        )
