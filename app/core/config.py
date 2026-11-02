import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    API_KEY = os.getenv("API_KEY")
    # Imprime cada consulta SQL; útil en desarrollo, demasiado ruido en la Pi
    SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"
    # Valida la firma del initData que Telegram envía a la Mini App del dashboard
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    # Orígenes del dashboard web, separados por coma
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200").split(",") if o.strip()]
