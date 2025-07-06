import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

# Database configuration
DATABASE_URL = "sqlite:///./assets/main.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
