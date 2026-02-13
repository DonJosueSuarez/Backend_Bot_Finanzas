from app.database.postgresql_connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from app.model.enums import TipoMovimiento

class TransactionORM(Base):
    __tablename__ = "transactions_back"
    
    id = Column(Integer, primary_key=True, index = True, autoincrement=True)
    tipo = Column(SAEnum(TipoMovimiento), nullable=False, default=TipoMovimiento.EGRESO)
    monto = Column(Numeric(precision=10, scale=2), nullable=False)
    descripcion = Column(String(255), nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user_id = Column(Integer, ForeignKey("users_back.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories_back.id"), nullable=False)
    
    user = relationship("UserORM", back_populates="transactions")
    category = relationship("CategoryORM", back_populates="transaction")