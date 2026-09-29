import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Default PostgreSQL URL. Can be overridden by DATABASE_URL environment variable.
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/trustlens"
)

# Resilient connection initialization
try:
    # Try PostgreSQL first
    if DATABASE_URL.startswith("postgresql"):
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        # Verify connection immediately to trigger fallback if offline
        with engine.connect() as conn:
            pass
    else:
        # Fallback/SQLite compatibility
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
        )
        with engine.connect() as conn:
            pass
except Exception as e:
    print(f"Connection verification failed for {DATABASE_URL}: {e}")
    print("Falling back to local SQLite database: sqlite:///./trustlens.db")
    DATABASE_URL = "sqlite:///./trustlens.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency injection helper to obtain database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
