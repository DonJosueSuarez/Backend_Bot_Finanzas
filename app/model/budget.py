from app.database.postgresql_connection import Base
from sqlalchemy import Column, Integer, Numeric, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship

class BudgetORM(Base):
    __tablename__ = "user_budgets_back"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    monto_mensual = Column(Numeric(10, 2), nullable=False)
    
    user_id = Column(Integer, ForeignKey("users_back.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories_back.id"), nullable=True)
    
    user = relationship("UserORM", back_populates="budgets")
    category = relationship("CategoryORM", back_populates="budgets")
    
    __table_args__ = (UniqueConstraint('user_id', 'category_id', name='_user_category_budget_uc'), Index('unique_global_budget', 'user_id', unique=True, postgresql_where=(category_id.is_(None))),)