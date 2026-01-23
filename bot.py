from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User, Settings
from config import BOT_TOKEN, ADMIN_TG_ID, WEBAPP_URL

Base.metadata.create_all(bind=engine)

def db() -> Session:
    return SessionLocal()

def ensure_settings():
    s = db().query(Settings).first()
    if not s:
        session = db()
        session.add(Settings())
        session.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_settings()

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("📦 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))
    ]])

    session = db()
    u = session.query(User).filter(User.tg_id == update.effective_user.id).first()

    if not u:
        context.user_data["reg"] = True
        await update.message.reply_text(
            "Nataobao 👋\n\n"
            "Регистрация:\n"
            "Отправьте одним сообщением:\n"
            "КОД Имя Фамилия\n\n"
            "Пример:\nNTB123 Иван Иванов",
            reply_markup=kb
        )
        return

    if u.role == "pending":
        await update.message.reply_text("⏳ Ваша заявка на рассмотрении админом.", reply_markup=kb)
        return

    await update.message.reply_text(f"✅ Добро пожаловать, {u.first_name}!", reply_markup=kb)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("reg"):
        return

    parts = update.message.text.strip().split()
    if len(parts) < 3:
        await update.message.reply_text("❌ Формат: КОД Имя Фамилия\nПример: NTB123 Иван Иванов")
        return

    code = parts[0].strip()
    first = parts[1].strip()
    last = " ".join(parts[2:]).strip()

    session = db()
    exists = session.query(User).filter(User.tg_id == update.effective_user.id).first()
    if exists:
        context.user_data.clear()
        await update.message.reply_text("Вы уже зарегистрированы. Напишите /start")
        return

    user = User(
        tg_id=update.effective_user.id,
        username=update.effective_user.username,
        role="pending",
        code=code,
        first_name=first,
        last_name=last
    )
    session.add(user)
    session.commit()

    if ADMIN_TG_ID:
        await context.bot.send_message(
            ADMIN_TG_ID,
            f"🔔 Заявка Nataobao\n"
            f"{first} {last}\n"
            f"Код: {code}\n"
            f"tg_id: {update.effective_user.id}\n"
            f"@{update.effective_user.username or '-'}"
        )

    context.user_data.clear()
    await update.message.reply_text("✅ Заявка отправлена админу. Ожидайте подтверждения. Напишите /start позже.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
