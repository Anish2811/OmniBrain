from fastapi import APIRouter

from backend.app.api.schemas import ChatRequest
from backend.app.api.schemas import ChatResponse

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    return ChatResponse(
        answer="RAG response will come here."
    )