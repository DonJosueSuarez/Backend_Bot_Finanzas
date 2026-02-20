from app.database.postgresql_connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum as SAEnum, Boolean
from sqlalchemy.sql import func
from app.model.enums import TipoMovimiento, TipoGasto

class TransactionORM(Base):
    __tablename__ = "transactions_back"
    
    id = Column(Integer, primary_key=True, index = True, autoincrement=True)
    tipo_movimiento = Column(SAEnum(TipoMovimiento), nullable=False)
    monto = Column(Numeric(precision=10, scale=2), nullable=False)
    descripcion = Column(String(255), nullable=False)
    tipo_gasto = Column(SAEnum(TipoGasto), nullable=True, default=TipoGasto.NECESIDAD)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_recurrente = Column(Boolean, nullable=False, default=False)
    
    user_id = Column(Integer, ForeignKey("users_back.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories_back.id"), nullable=True)
    
    user = relationship("UserORM", back_populates="transactions")
    category = relationship("CategoryORM", back_populates="transaction")