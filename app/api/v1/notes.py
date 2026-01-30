from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.services.note_service import create_note, get_note, list_notes, update_note, delete_note
from app.api.deps import get_db, get_current_user_dep
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note_endpoint(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Create a new note with automatic embedding generation.
    
    - **title**: Note title (required)
    - **content**: Note content (required)
    - **tags**: Optional list of tags
    """
    note = create_note(db, note_data, current_user)
    return note


@router.get("/", response_model=List[NoteResponse])
def list_notes_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    List all notes for the authenticated user with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100)
    """
    notes = list_notes(db, current_user, skip, limit)
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
def get_note_endpoint(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Get a specific note by ID.
    
    Returns 404 if note doesn't exist or user doesn't own it.
    """
    note = get_note(db, note_id, current_user)
    return note


@router.put("/{note_id}", response_model=NoteResponse)
def update_note_endpoint(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Update a note. Regenerates embedding if title or content changed.
    
    All fields are optional - only provided fields are updated.
    """
    note = update_note(db, note_id, note_data, current_user)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_endpoint(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """
    Delete a note permanently.
    
    Returns 204 No Content on success.
    """
    delete_note(db, note_id, current_user)
    return None