from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.postgresql_connection import Base
from sqlalchemy import Column, Integer, String, DateTime

class UserORM(Base):
    __tablename__ = "users_back"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    telegram_id = Column(String(20), unique=True, nullable=True)
    telefono = Column(String(20), unique=True, nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    transactions = relationship("TransactionORM", back_populates="user")
    budgets = relationship("BudgetORM", back_populates="user")