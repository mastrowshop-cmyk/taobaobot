import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_TG_ID = int(os.getenv("ADMIN_TG_ID", "0"))
WEBAPP_URL = os.getenv("WEBAPP_URL", "")

# Render Postgres обычно даёт DATABASE_URL, либо оставь пустым и будет SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nataobao.db")

# CORS (для GitHub Pages WebApp)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
