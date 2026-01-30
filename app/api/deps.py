from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.security import decode_access_token
from app.services.auth_service import get_current_user
from app.models.user import User

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Yields a session and ensures it's closed after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate JWT token, return current user.
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
    
    Returns:
        Current user
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    try:
        user = get_current_user(db, int(user_id))
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )