from sqlalchemy import func
from decimal import Decimal
from app.model.transaction import TransactionORM
from sqlalchemy.orm import Session
from app.repository.base_financial_repository import IFinancialRepository
from typing import Dict

class PostgresFinancialRepository(IFinancialRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def get_totals_by_type(self, user_id: int) -> Dict[str, Decimal]:
        result = (self.db.query(
                    TransactionORM.tipo, 
                    func.sum(TransactionORM.monto).label('total')
                )
                .filter(TransactionORM.user_id == user_id)
                .group_by(TransactionORM.tipo)
                .all())
        
        totals = {"INGRESO": Decimal(0), "EGRESO": Decimal(0)}
        
        for r in result:
            totals[r.tipo.value] = r.total
            
        return totals