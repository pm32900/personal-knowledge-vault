from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.schemas.note import NoteSearchResult, NoteResponse
from app.services.rag_service import semantic_search
from app.api.deps import get_db, get_current_user_dep
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[NoteSearchResult])
def search_notes(
    query: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Semantic search across user's notes using vector similarity.
    
    - **query**: Search query (natural language)
    - **top_k**: Number of results (1-20, default: 5)
    
    Returns notes ranked by semantic similarity with scores.
    """
    results = semantic_search(db, query, current_user, top_k)
    
    # Convert to response format
    search_results = []
    for result in results:
        note_response = NoteResponse(
            id=result["note_id"],
            title=result["title"],
            content=result["content"],
            tags=result["tags"],
            user_id=current_user.id,
            created_at=result.get("created_at"),
            updated_at=result.get("updated_at")
        )
        search_results.append(NoteSearchResult(
            note=note_response,
            similarity=result["similarity"],
            excerpt=result["excerpt"]
        ))
    
    return search_results