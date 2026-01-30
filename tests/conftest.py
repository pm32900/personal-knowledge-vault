import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test_temp.db"

from app.database import Base, get_db
from app.models.user import User
from app.main import app


@pytest.fixture(scope="function", autouse=True)
def cleanup_db():
    """Clean up database file and dispose module-level engine before each test."""
    import app.database as db_module
    
    # Dispose the module-level engine to close all connections
    db_module.engine.dispose()
    
    # Clean up any existing database file
    db_file = Path("./test_temp.db")
    if db_file.exists():
        db_file.unlink()
    
    yield
    
    # Clean up after test
    db_module.engine.dispose()
    if db_file.exists():
        db_file.unlink()


@pytest.fixture(scope="function")
def db_session(cleanup_db):
    """Create a fresh database for each test."""
    import app.database as db_module
    
    db_file = Path("./test_temp.db")
    
    # Create engine with file-based SQLite
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Replace the module-level engine temporarily
    original_engine = db_module.engine
    db_module.engine = engine
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Clean up
    session.close()
    engine.dispose()
    
    # Restore original engine
    db_module.engine = original_engine


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}