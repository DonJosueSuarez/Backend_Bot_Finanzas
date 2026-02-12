from app.database.postgresql_connection import Base
from sqlalchemy import create_engine, Column, Integer, String

class UserORM(Base):
    __tablename__ = "users_back"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) #Chat ID
    nombre = Column(String(50), nullable=False)
    telegram_id = Column(String(20), unique=True, nullable=True)
    telefono = Column(String(20), unique=True, nullable=True)
    
