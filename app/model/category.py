from app.database.postgresql_connection import Base
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.model.enums import TipoCategoria

class CategoryORM(Base):
    __tablename__ = "categories_back"
    
    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    nombre = Column(SAEnum(TipoCategoria), nullable=False)
    color = Column(String(100), nullable=True)
    image = Column(String(300), nullable=True)
    
    transaction = relationship("TransactionORM", back_populates="category")
    budgets = relationship("BudgetORM", back_populates="user")