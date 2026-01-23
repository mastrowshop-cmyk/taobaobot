from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

# =====================
# USERS
# =====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(64), nullable=True)

    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)

    code = Column(String(32), unique=True, index=True, nullable=False)

    role = Column(String(16), default="pending")  
    # pending | client | operator | admin

    created_at = Column(DateTime, default=datetime.utcnow)

    parcels = relationship("Parcel", back_populates="user")

# =====================
# PARCELS
# =====================
class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)
    track = Column(String(128), nullable=True)

    status = Column(String(32), default="china")
    # china | ussuriysk | yakutsk | pay | paid | shipped

    weight_kg = Column(Float, nullable=True)
    price_rub = Column(Float, nullable=True)

    paid = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="parcels")

# =====================
# SETTINGS (ADMIN)
# =====================
class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)

    price_per_kg = Column(Float, default=500)

    pay_text = Column(Text, default="Инструкция по оплате")

    support_username = Column(String(64), default="support")

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
