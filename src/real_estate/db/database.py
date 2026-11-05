"""
Database connection and session management for Real Estate Intelligence Engine.
Ensures an independent SQLite connection to data/real_estate.db.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.real_estate.config import REAL_ESTATE_DATABASE_URL

engine = create_engine(
    REAL_ESTATE_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in REAL_ESTATE_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_real_estate_engine():
    """Return the SQLAlchemy engine for real_estate.db."""
    return engine


def get_real_estate_db():
    """FastAPI dependency for obtaining a real estate database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
