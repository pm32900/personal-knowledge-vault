from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.rag_service import ask_vault
from app.api.deps import get_db, get_current_user_dep
from app.models.user import User

router = APIRouter()


class Citation(BaseModel):
    """Citation schema for RAG response."""
    note_id: int
    title: str
    excerpt: str
    similarity: float


class RAGResponse(BaseModel):
    """RAG response with answer and citations."""
    answer: str
    citations: List[Citation]


@router.post("/ask", response_model=RAGResponse)
def ask_question(
    query: str = Query(..., min_length=1, description="Question to ask"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Ask a question about your notes and get an AI-generated answer with citations.
    
    - **query**: Natural language question
    
    Returns:
    - **answer**: AI-generated answer based on your notes
    - **citations**: Source notes with similarity scores and excerpts
    
    Example: "What did I learn about machine learning?"
    """
    result = ask_vault(db, query, current_user)
    
    # Convert citations to response format
    citations = [
        Citation(
            note_id=c["note_id"],
            title=c["title"],
            excerpt=c["excerpt"],
            similarity=c["similarity"]
        )
        for c in result["citations"]
    ]
    
    return RAGResponse(
        answer=result["answer"],
        citations=citations
    )