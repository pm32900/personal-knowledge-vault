from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.services.embedding_service import get_embedding_service
from app.core.exceptions import NotFoundError, AuthorizationError, AIServiceError
from app.logging_config import get_logger

logger = get_logger(__name__)


def create_note(db: Session, note_data: NoteCreate, user: User) -> Note:
    """
    Create a new note with embedding.
    
    Args:
        db: Database session
        note_data: Note creation data
        user: Owner user
    
    Returns:
        Created note
    """
    # Create note
    note = Note(
        title=note_data.title,
        content=note_data.content,
        tags=note_data.tags,
        user_id=user.id
    )
    
    # Generate embedding
    try:
        embedding_service = get_embedding_service()
        combined_text = f"{note_data.title}\n{note_data.content}"
        embedding = embedding_service.embed_text(combined_text)
        note.embedding = embedding
        logger.info("embedding_generated", note_title=note_data.title)
    except AIServiceError as e:
        logger.warning("embedding_failed", error=str(e), note_title=note_data.title)
        # Note is still created without embedding
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    logger.info("note_created", note_id=note.id, user_id=user.id)
    return note


def get_note(db: Session, note_id: int, user: User) -> Note:
    """
    Get a note by ID.
    
    Args:
        db: Database session
        note_id: Note ID
        user: Requesting user
    
    Returns:
        Note object
    
    Raises:
        NotFoundError: If note doesn't exist
        AuthorizationError: If user doesn't own the note
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if not note:
        raise NotFoundError(f"Note {note_id} not found")
    
    if note.user_id != user.id:
        raise AuthorizationError("You don't have permission to access this note")
    
    return note


def list_notes(db: Session, user: User, skip: int = 0, limit: int = 100) -> List[Note]:
    """
    List user's notes with pagination.
    
    Args:
        db: Database session
        user: Requesting user
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of notes
    """
    notes = db.query(Note)\
        .filter(Note.user_id == user.id)\
        .order_by(Note.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return notes


def update_note(db: Session, note_id: int, note_data: NoteUpdate, user: User) -> Note:
    """
    Update a note and regenerate embedding if content changed.
    
    Args:
        db: Database session
        note_id: Note ID
        note_data: Update data
        user: Requesting user
    
    Returns:
        Updated note
    """
    note = get_note(db, note_id, user)
    
    # Track if content changed
    content_changed = False
    
    # Update fields
    if note_data.title is not None:
        note.title = note_data.title
        content_changed = True
    
    if note_data.content is not None:
        note.content = note_data.content
        content_changed = True
    
    if note_data.tags is not None:
        note.tags = note_data.tags
    
    # Regenerate embedding if content changed
    if content_changed:
        try:
            embedding_service = get_embedding_service()
            combined_text = f"{note.title}\n{note.content}"
            embedding = embedding_service.embed_text(combined_text)
            note.embedding = embedding
            logger.info("embedding_regenerated", note_id=note.id)
        except AIServiceError as e:
            logger.warning("embedding_regeneration_failed", error=str(e), note_id=note.id)
    
    db.commit()
    db.refresh(note)
    
    logger.info("note_updated", note_id=note.id, user_id=user.id)
    return note


def delete_note(db: Session, note_id: int, user: User) -> None:
    """
    Delete a note.
    
    Args:
        db: Database session
        note_id: Note ID
        user: Requesting user
    """
    note = get_note(db, note_id, user)
    
    db.delete(note)
    db.commit()
    
    logger.info("note_deleted", note_id=note_id, user_id=user.id)