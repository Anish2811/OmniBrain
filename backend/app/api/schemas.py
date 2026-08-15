from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        description="User's natural language question",
    )
    session_id: Optional[str] = None
    top_k: int = 5


class SourceCitation(BaseModel):
    source_type: str
    content_snippet: str

    document: Optional[str] = None
    document_path: Optional[str] = None
    chunk_id: Optional[int] = None

    page_number: Optional[int] = None
    word_start: Optional[int] = None
    word_end: Optional[int] = None

    score: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    citations: List[SourceCitation]
    agent_trace: List[str]