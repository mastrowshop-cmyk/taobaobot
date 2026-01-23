import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User, Parcel, Settings

# =====================
# APP
# =====================
app = FastAPI(title="Nataobao API")

# =====================
# CORS (ОБЯЗАТЕЛЬНО)
# =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Telegram WebApp + GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# DB INIT
# =====================
Base.metadata.create_all(bind=engine)

# =====================
# HEALTH CHECK
# =====================
@app.get("/health")
def health():
    return {"ok": True}

# =====================
# HELPERS
# =====================
def get_me(initData: str, db: Session):
    """
    УПРОЩЁННО:
    Сейчас просто ищем пользователя по tg_id,
    позже можно добавить реальную валидацию initData
    """
    try:
        tg_id = int(initData)
    except:
        raise HTTPException(status_code=403, detail="Invalid initData")

    user = db.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        raise HTTPException(status_code=403, detail="Not registered")
    return user

# =====================
# AUTH / PROFILE
# =====================
@app.post("/me")
def me(data: dict, db: Session = Depends(get_db)):
    initData = data.get("initData")
    user = get_me(initData, db)

    return {
        "tg_id": user.tg_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "code": user.code,
        "role": user.role,
        "support_username": get_settings(db).support_username,
    }


@app.post("/profile/update")
def update_profile(data: dict, db: Session = Depends(get_db)):
    user = get_me(data.get("initData"), db)

    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)

    db.commit()
    return {"ok": True}

# =====================
# PARCELS
# =====================
@app.post("/parcels/list")
def parcels_list(data: dict, db: Session = Depends(get_db)):
    user = get_me(data.get("initData"), db)

    parcels = db.query(Parcel).filter(Parcel.user_id == user.id).all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "track": p.track,
            "status": p.status,
            "weight_kg": p.weight_kg,
            "price_rub": p.price_rub,
            "paid": p.paid,
        }
        for p in parcels
    ]

# =====================
# PAYMENT
# =====================
def get_settings(db: Session):
    s = db.query(Settings).first()
    if not s:
        s = Settings(price_per_kg=500, pay_text="Инструкция по оплате", support_username="support")
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


@app.post("/payment/info")
def payment_info(data: dict, db: Session = Depends(get_db)):
    get_me(data.get("initData"), db)
    s = get_settings(db)
    return {"pay_text": s.pay_text}

# =====================
# OPERATOR
# =====================
@app.post("/operator/weigh")
def operator_weigh(data: dict, db: Session = Depends(get_db)):
    operator = get_me(data.get("initData"), db)
    if operator.role not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    code = data["code"]
    parcel_id = data["parcel_id"]
    weight_kg = float(data["weight_kg"])

    user = db.query(User).filter(User.code == code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    parcel = db.query(Parcel).filter(Parcel.id == parcel_id, Parcel.user_id == user.id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    settings = get_settings(db)
    parcel.weight_kg = weight_kg
    parcel.price_rub = round(weight_kg * settings.price_per_kg)
    parcel.status = "pay"

    db.commit()
    return {"price_rub": parcel.price_rub}

# =====================
# ADMIN
# =====================
@app.post("/admin/settings/get")
def admin_settings_get(data: dict, db: Session = Depends(get_db)):
    admin = get_me(data.get("initData"), db)
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    s = get_settings(db)
    return {
        "price_per_kg": s.price_per_kg,
        "pay_text": s.pay_text,
        "support_username": s.support_username,
    }


@app.post("/admin/settings/save")
def admin_settings_save(data: dict, db: Session = Depends(get_db)):
    admin = get_me(data.get("initData"), db)
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    s = get_settings(db)
    s.price_per_kg = float(data["price_per_kg"])
    s.pay_text = data["pay_text"]
    s.support_username = data["support_username"]

    db.commit()
    return {"ok": True}
