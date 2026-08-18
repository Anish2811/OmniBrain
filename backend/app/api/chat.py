from fastapi import APIRouter, HTTPException
from openai import OpenAI
import openai

from backend.app.api.schemas import QueryRequest
from backend.app.api.schemas import QueryResponse
from backend.app.api.schemas import SourceCitation

from Config.Config import settings
from backend.app.agents.graph import omnibrain_graph
from backend.app.observability.langfuse import trace_request


router = APIRouter(tags=["Chat"])


def _generate_rag_answer(
    query: str,
    context: str,
) -> str:

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


def _build_search_citations(
    results,
) -> list:

    citations = []

    for result in results:
        metadata = result.get(
            "metadata",
            {},
        )

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
                document=metadata.get(
                    "document"
                ),
                document_path=metadata.get(
                    "document_path"
                ),
                chunk_id=metadata.get(
                    "chunk_id"
                ),
                page_number=metadata.get(
                    "page_number"
                ),
                word_start=metadata.get(
                    "word_start"
                ),
                word_end=metadata.get(
                    "word_end"
                ),
                score=result.get(
                    "score"
                ),
            )
        )

    return citations


def _build_vision_citations(
    citations,
) -> list:

    response_citations = []

    for citation in citations:
        response_citations.append(
            SourceCitation(
                source_type=citation.get(
                    "source_type",
                    "image",
                ),
                content_snippet=citation.get(
                    "content_snippet",
                    "",
                )[:500],
                document=citation.get(
                    "filename"
                ),
                document_path=citation.get(
                    "image_path"
                ),
                page_number=citation.get(
                    "page_number"
                ),
                score=citation.get(
                    "score"
                ),
            )
        )

    return response_citations


@router.post(
    "/chat",
    response_model=QueryResponse,
)
async def chat(
    request: QueryRequest,
):

    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    try:

        with trace_request(
            name="omnibrain-chat",
            metadata={
                "top_k": request.top_k,
            },
        ) as trace:

            if trace is not None:
                trace.update(
                    input={
                        "query": request.query.strip(),
                    }
                )

            graph_result = omnibrain_graph.invoke(
                {
                    "query": request.query.strip(),
                    "top_k": request.top_k,
                }
            )

            if trace is not None:
                trace.update(
                    output={
                        "route": graph_result.get(
                            "route",
                            "unknown",
                        ),
                        "agent_trace": graph_result.get(
                            "agent_trace",
                            [],
                        ),
                    }
                )

        route = graph_result.get(
            "route",
            "search",
        )

        results = graph_result.get(
            "results",
            [],
        )

        context = graph_result.get(
            "context",
            "",
        )

        agent_trace = list(
            graph_result.get(
                "agent_trace",
                [],
            )
        )

        answer = graph_result.get(
            "answer",
            "",
        )

        citations = []

        if route == "search":

            # Check if guardrail blocked the query
            if graph_result.get("error") == "Query is outside document scope.":
                return QueryResponse(
                    answer=answer,
                    citations=[],
                    agent_trace=agent_trace,
                )

            if not results:
                return QueryResponse(
                    answer=(
                        "I could not find relevant information "
                        "in the uploaded documents."
                    ),
                    citations=[],
                    agent_trace=agent_trace + [
                        "no_results",
                    ],
                )

            if not context:
                raise RuntimeError(
                    "Retrieved documents contain no usable text."
                )

            answer = _generate_rag_answer(
                request.query.strip(),
                context,
            )

            citations = _build_search_citations(
                results
            )

            agent_trace.extend(
                [
                    "llm",
                    "rag",
                ]
            )

        elif route == "vision":

            citations = _build_vision_citations(
                graph_result.get(
                    "citations",
                    [],
                )
            )

            if not answer:
                answer = (
                    "I could not analyze the requested "
                    "image."
                )

        elif route == "sql":

            if not answer:
                answer = str(
                    results
                )

        else:

            answer = (
                answer
                or "Unable to process the request."
            )

        return QueryResponse(
            answer=answer,
            citations=citations,
            agent_trace=agent_trace,
        )

    except HTTPException:
        raise

    except openai.AuthenticationError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The LLM service authentication "
                "is unavailable."
            ),
        )

    except openai.RateLimitError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The LLM service quota or rate "
                "limit has been reached."
            ),
        )

    except openai.APIConnectionError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The LLM service is temporarily "
                "unavailable."
            ),
        )

    except openai.APIStatusError:
        raise HTTPException(
            status_code=502,
            detail=(
                "The LLM service returned an error."
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "OmniBrain failed to process "
                "the request."
            ),
        )