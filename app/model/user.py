from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, column_property
from app.database.postgresql_connection import Base
from sqlalchemy import Column, Integer, String, DateTime, exists
from app.model.transaction import TransactionORM

class UserORM(Base):
    __tablename__ = "users_back"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    telegram_id = Column(String(20), unique=True, nullable=True)
    # telefono = Column(String(20), unique=True, nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # El saldo inicial se registra como la primera transacción (un INGRESO),
    # así que basta con saber si el usuario ya tiene alguna. Se calcula en SQL.
    tiene_saldo_inicial = column_property(exists().where(TransactionORM.user_id == id).correlate_except(TransactionORM))

    transactions = relationship("TransactionORM", back_populates="user")
    budgets = relationship("BudgetORM", back_populates="user")