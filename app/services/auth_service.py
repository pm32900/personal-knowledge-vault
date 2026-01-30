from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import AuthenticationError, ValidationError
from app.logging_config import get_logger

logger = get_logger(__name__)


def register_user(db: Session, user_data: UserCreate) -> User:
    """
    Register a new user.
    
    Args:
        db: Database session
        user_data: User registration data
    
    Returns:
        Created user
    
    Raises:
        ValidationError: If email already exists
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning("registration_failed", email=user_data.email, reason="email_exists")
        raise ValidationError("Email already registered")
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info("user_registered", user_id=user.id, email=user.email)
    return user


def authenticate_user(db: Session, login_data: UserLogin) -> Token:
    """
    Authenticate user and return JWT token.
    
    Args:
        db: Database session
        login_data: Login credentials
    
    Returns:
        JWT token
    
    Raises:
        AuthenticationError: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        logger.warning("login_failed", email=login_data.email, reason="user_not_found")
        raise AuthenticationError("Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        logger.warning("login_failed", email=login_data.email, reason="wrong_password")
        raise AuthenticationError("Invalid email or password")
    
    # Check if user is active
    if not user.is_active:
        logger.warning("login_failed", email=login_data.email, reason="inactive_user")
        raise AuthenticationError("Account is inactive")
    
    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    logger.info("user_logged_in", user_id=user.id, email=user.email)
    return Token(access_token=access_token)


def get_current_user(db: Session, user_id: int) -> User:
    """
    Get user by ID from token.
    
    Args:
        db: Database session
        user_id: User ID from decoded token
    
    Returns:
        User object
    
    Raises:
        AuthenticationError: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthenticationError("User not found")
    
    if not user.is_active:
        raise AuthenticationError("Account is inactive")
    
    return user