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
    Perform semantic search on user's notes.
    
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
    
    # Generate query embedding
    try:
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.embed_text(query)
    except AIServiceError as e:
        logger.error("query_embedding_failed", error=str(e))
        raise AIServiceError("Failed to process search query")
    
    # Perform vector similarity search
    # Using cosine similarity: 1 - (embedding <=> query_embedding)
    sql = text("""
        SELECT 
            id,
            title,
            content,
            tags,
            user_id,
            created_at,
            updated_at,
            1 - (embedding <=> :query_embedding) as similarity
        FROM notes
        WHERE user_id = :user_id
        AND embedding IS NOT NULL
        ORDER BY embedding <=> :query_embedding
        LIMIT :top_k
    """)
    
    result = db.execute(
        sql,
        {
            "query_embedding": str(query_embedding),
            "user_id": user.id,
            "top_k": top_k
        }
    )
    
    results = []
    for row in result:
        # Create excerpt (first 200 chars of content)
        excerpt = row.content[:200] + "..." if len(row.content) > 200 else row.content
        
        results.append({
            "note_id": row.id,
            "title": row.title,
            "content": row.content,
            "tags": row.tags,
            "similarity": float(row.similarity),
            "excerpt": excerpt
        })
    
    logger.info("semantic_search", user_id=user.id, query=query, results_count=len(results))
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