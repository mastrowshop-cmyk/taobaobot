from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    role = Column(String, default="pending")  # pending, client, operator, admin
    code = Column(String)
    name = Column(String)

class Parcel(Base):
    __tablename__ = "parcels"
    id = Column(Integer, primary_key=True)
    user_code = Column(String)
    description = Column(String)
    status = Column(String, default="china")
    weight = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    paid = Column(Boolean, default=False)

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    price_per_kg = Column(Float, default=800)
    pay_text = Column(String, default="Оплата по карте **** **** **** 1234")
