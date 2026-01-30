from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import register_user, authenticate_user
from app.api.deps import get_db

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    """
    user = register_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login and receive JWT access token.
    
    - **email**: Registered email
    - **password**: User password
    
    Returns JWT token to use in Authorization header: `Bearer <token>`
    """
    token = authenticate_user(db, login_data)
    return token