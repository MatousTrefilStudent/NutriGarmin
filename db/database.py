from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database file location (creates app.db in the root folder)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# connect_args={"check_same_thread": False} is required for SQLite with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session factory for DB transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# FastAPI dependency to inject DB sessions into route handlers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()