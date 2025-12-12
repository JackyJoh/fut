from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import text
from .config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def create_db_and_tables():
    """
    Initializes the database by creating all tables defined in your models.
    """
    # Ensure dedicated schema exists and use it for our tables
    with engine.connect() as conn:
        # Create schema if not exists (owned by current user)
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS fut"))
        # Set search_path so unqualified table names go into 'fut'
        conn.execute(text("SET search_path TO fut"))
        conn.commit()

    # Create tables within the 'fut' schema via search_path
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    A dependency function for FastAPI to manage database connections per request.
    """
    with Session(engine) as session:
        yield session