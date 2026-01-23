from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

def _fix_db_url(url: str) -> str:
    # Render иногда даёт postgres://, SQLAlchemy ждёт postgresql+psycopg2://
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url

DB_URL = _fix_db_url(DATABASE_URL)

connect_args = {}
if DB_URL.startswith("sqlite:///"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DB_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
