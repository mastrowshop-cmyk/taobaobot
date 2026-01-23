import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

raw = os.getenv("DATABASE_URL")
if not raw:
    raise RuntimeError("DATABASE_URL is not set")

# 1) нормализуем схему под psycopg3
# возможные случаи:
# postgresql://...
# postgres://...
# postgresql+psycopg2://...   (если где-то старое осталось)
if raw.startswith("postgresql+psycopg2://"):
    raw = raw.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
elif raw.startswith("postgresql://"):
    raw = raw.replace("postgresql://", "postgresql+psycopg://", 1)
elif raw.startswith("postgres://"):
    raw = raw.replace("postgres://", "postgresql+psycopg://", 1)

# 2) добавим sslmode=require если его нет (Supabase обычно требует)
u = urlparse(raw)
q = dict(parse_qsl(u.query))
if "sslmode" not in q:
    q["sslmode"] = "require"
raw = urlunparse(u._replace(query=urlencode(q)))

print("DB_URL_EFFECTIVE:", raw)  # посмотри в Render Logs

engine = create_engine(
    raw,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
