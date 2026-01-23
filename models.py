from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)

    tg_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)

    role = Column(String, default="pending")  # pending, client, operator, admin
    code = Column(String, index=True, nullable=False)  # персональный код
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Parcel(Base):
    __tablename__ = "parcels"
    id = Column(Integer, primary_key=True)

    user_code = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)      # описание
    track = Column(String, nullable=True)       # трек/скан

    # статусы по ТЗ (3 точки только для отображения, работаем с Якутском)
    status = Column(String, default="china")    # china/ussuriysk/yakutsk/pay/paid/shipped

    weight_kg = Column(Float, nullable=True)
    price_rub = Column(Float, nullable=True)
    paid = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)

    price_per_kg = Column(Float, default=800.0)  # тариф
    pay_text = Column(Text, default="Оплата: переведите сумму ... (редактирует админ)")
    support_username = Column(String, default="YOUR_SUPPORT")  # без @
