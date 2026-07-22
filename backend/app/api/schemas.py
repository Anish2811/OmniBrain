from pydantic import BaseModel, Field
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str = Field(..., description="User's natural language question")
    session_id: Optional[str] = None
    top_k: int = 5

class SourceCitation(BaseModel):
    source_type: str  # "text", "table", "chart", "sql"
    content_snippet: str
    page_number: Optional[int] = None
    score: Optional[float] = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[SourceCitation]
    agent_trace: List[str]  # which agents fired, for transparency