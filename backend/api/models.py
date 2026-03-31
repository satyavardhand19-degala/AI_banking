# Vaani AI Banking Intelligence — API Models

from pydantic import BaseModel, Field
from typing import Optional, List, Any

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)

class SpeakRequest(BaseModel):
    text: str = Field(..., max_length=1000)
    language_code: str = "en-IN"

class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    columns: List[str] = []
    rows: List[List[Any]] = []
    count: int = 0
    summary: Optional[str] = None
    error: Optional[str] = None
