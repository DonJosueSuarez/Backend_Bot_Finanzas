import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    API_KEY = os.getenv("API_KEY")
    # Imprime cada consulta SQL; útil en desarrollo, demasiado ruido en la Pi
    SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"