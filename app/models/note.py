from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
from app.database import Base
from app.config import settings


class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), default=list)
    
    # Vector embedding for semantic search
    embedding = Column(Vector(settings.VECTOR_DIMENSIONS), nullable=True)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    owner = relationship("User", back_populates="notes")
    
    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title[:30]})>"