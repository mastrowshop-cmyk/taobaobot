from fastapi import FastAPI
from database import Base, engine, SessionLocal
from models import User, Parcel, Settings
from bot import run_bot

Base.metadata.create_all(bind=engine)

db = SessionLocal()
if not db.query(Settings).first():
    db.add(Settings())
    db.commit()

run_bot()

