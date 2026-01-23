import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# =========================================
# DATABASE URL
# =========================================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# =========================================
# Normalize URL for SQLAlchemy + psycopg3
# - Supabase gives: postgresql://...
# - SQLAlchemy needs: postgresql+psycopg://...
# =========================================
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

# =========================================
# ENGINE
# =========================================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    future=False,  # для SQLAlchemy 1.4 можно не трогать, но так стабильнее
)

# =========================================
# SESSION
# =========================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# =========================================
# BASE
# =========================================
Base = declarative_base()

# =========================================
# DEPENDENCY
# =========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

