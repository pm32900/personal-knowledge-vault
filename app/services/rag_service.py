from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import openai
from app.models.note import Note
from app.models.user import User
from app.services.embedding_service import get_embedding_service
from app.core.exceptions import AIServiceError
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def semantic_search(
    db: Session,
    query: str,
    user: User,
    top_k: int = None
) -> List[Dict[str, Any]]:
    """
    Search user's notes. Uses text matching as fallback when pgvector is unavailable.
    
    Args:
        db: Database session
        query: Search query
        user: Requesting user
        top_k: Number of results (defaults to config value)
    
    Returns:
        List of dicts with note, similarity, and excerpt
    """
    if top_k is None:
        top_k = settings.TOP_K_RESULTS
    
    # Text-based search fallback (pgvector not installed)
    # Search by keyword matching in title and content
    query_lower = query.lower()
    keywords = [kw.strip() for kw in query_lower.split() if len(kw.strip()) > 2]
    
    notes = db.query(Note)\
        .filter(Note.user_id == user.id)\
        .order_by(Note.updated_at.desc())\
        .limit(top_k * 3)\
        .all()
    
    scored_notes = []
    for note in notes:
        text_blob = f"{note.title} {note.content}".lower()
        matches = sum(1 for kw in keywords if kw in text_blob)
        if matches > 0 or not keywords:
            score = matches / max(len(keywords), 1)
            scored_notes.append((note, score))
    
    # Sort by score descending, take top_k
    scored_notes.sort(key=lambda x: x[1], reverse=True)
    scored_notes = scored_notes[:top_k]
    
    results = []
    for note, score in scored_notes:
        excerpt = note.content[:200] + "..." if len(note.content) > 200 else note.content
        results.append({
            "note_id": note.id,
            "title": note.title,
            "content": note.content,
            "tags": note.tags or [],
            "similarity": min(score, 1.0),
            "excerpt": excerpt,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
        })
    
    logger.info("text_search", user_id=user.id, query=query, results_count=len(results))
    return results


def ask_vault(db: Session, query: str, user: User) -> Dict[str, Any]:
    """
    RAG pipeline: retrieve relevant notes and generate answer with citations.
    
    Args:
        db: Database session
        query: User question
        user: Requesting user
    
    Returns:
        Dict with answer and citations
    """
    # Step 1: Retrieve relevant notes
    search_results = semantic_search(db, query, user, top_k=settings.TOP_K_RESULTS)
    
    if not search_results:
        return {
            "answer": "I couldn't find any relevant notes to answer your question.",
            "citations": []
        }
    
    # Step 2: Build context from retrieved notes
    context_parts = []
    citations = []
    
    for idx, result in enumerate(search_results, 1):
        context_parts.append(f"[{idx}] {result['title']}\n{result['content']}\n")
        citations.append({
            "note_id": result["note_id"],
            "title": result["title"],
            "excerpt": result["excerpt"],
            "similarity": result["similarity"]
        })
    
    context = "\n".join(context_parts)
    
    # Step 3: Generate answer with OpenAI
    if not settings.is_openai_configured:
        return {
            "answer": "AI service is not configured. Please set OPENAI_API_KEY.",
            "citations": citations
        }
    
    try:
        openai.api_key = settings.OPENAI_API_KEY
        
        prompt = f"""You are a helpful assistant that answers questions based on the user's personal notes.

Context from notes:
{context}

User question: {query}

Instructions:
- Answer the question using ONLY information from the provided notes
- Reference notes using [1], [2], etc. when citing information
- If the notes don't contain enough information, say so
- Be concise and accurate

Answer:"""

        response = openai.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on personal notes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        logger.info("rag_completed", user_id=user.id, query=query, citations_count=len(citations))
        
        return {
            "answer": answer,
            "citations": citations
        }
        
    except Exception as e:
        logger.error("rag_generation_failed", error=str(e), user_id=user.id)
        raise AIServiceError(f"Failed to generate answer: {str(e)}")