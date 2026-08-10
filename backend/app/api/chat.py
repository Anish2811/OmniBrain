from fastapi import APIRouter

from backend.app.api.schemas import QueryRequest
from backend.app.api.schemas import QueryResponse

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):

    return QueryResponse(
        answer="RAG response generation is not connected yet.",
        citations=[],
        agent_trace=[],
    )