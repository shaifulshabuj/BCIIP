from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class EntitySchema(BaseModel):
    id: UUID
    text: str
    type: str

    class Config:
        from_attributes = True

class ArticleResponse(BaseModel):
    id: UUID
    source: str
    title: str
    url: str
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    language: Optional[str] = None
    primary_category: Optional[str] = None
    topic_confidence: Optional[str] = None
    summary_text: Optional[str] = None
    summary_bullets: Optional[str] = None
    entities: List[EntitySchema] = []

    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    query: str
    type: str = "text" # "text" or "semantic"
    limit: int = 10
