from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import StaticPool
from app.config import settings
import os

# Use different engine configuration for SQLite (tests) vs PostgreSQL (production)
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    import os
    from sqlalchemy import text
    import logging
    logger = logging.getLogger(__name__)
    
    # Skip database initialization during tests
    if os.getenv("ENVIRONMENT") == "testing":
        logger.info("Skipping database initialization in test environment")
        return

    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("pgvector extension created successfully")
    except Exception as e:
        logger.warning(f"Could not create pgvector extension: {e}. Vector search features will be disabled.")

    from app.models import user, note

    Base.metadata.create_all(bind=engine)
    