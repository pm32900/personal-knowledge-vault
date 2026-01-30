from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class NoteCreate(BaseModel):
    """Schema for creating a note."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    """Schema for note response."""
    id: int
    title: str
    content: str
    tags: List[str]
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteSearchResult(BaseModel):
    """Schema for semantic search results with similarity score."""
    note: NoteResponse
    similarity: float = Field(..., ge=0.0, le=1.0)
    excerpt: str  # Relevant content snippet