from sqlalchemy import func
from decimal import Decimal
from app.model.transaction import TransactionORM
from app.model.category import CategoryORM
from app.model.enums import TipoMovimiento, TipoGasto
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.repository.base_financial_repository import IFinancialRepository
from typing import Dict

class PostgresFinancialRepository(IFinancialRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def get_totals_by_type(self, user_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Decimal]:
        result = (self.db.query(
                    TransactionORM.tipo_movimiento, 
                    func.sum(TransactionORM.monto).label('total')
                )
                .filter(TransactionORM.user_id == user_id,
                        TransactionORM.fecha >= fecha_inicio,
                        TransactionORM.fecha <= fecha_fin)
                .group_by(TransactionORM.tipo_movimiento)
                .all())
        
        totals = {"INGRESO": Decimal(0), "EGRESO": Decimal(0)}
        
        for r in result:
            totals[r.tipo_movimiento.value] = r.total
            
        return totals
    
    def get_total_balance_to_date(self, user_id: int, fecha_corte: datetime) -> Decimal:
        """Calcula el saldo acumulado desde el inicio de los tiempos hasta la fecha_fin."""
        ingresos = (self.db.query(func.sum(TransactionORM.monto))
                    .filter(
                        TransactionORM.user_id == user_id,
                        TransactionORM.tipo_movimiento == "INGRESO",
                        TransactionORM.fecha <= fecha_corte
                    ).scalar()) or Decimal(0)
                    
        egresos = (self.db.query(func.sum(TransactionORM.monto))
                .filter(
                    TransactionORM.user_id == user_id,
                    TransactionORM.tipo_movimiento == "EGRESO",
                    TransactionORM.fecha <= fecha_corte
                ).scalar()) or Decimal(0)
                
        return ingresos - egresos
    
    def get_essential_spending_last_90_days(self, user_id: int) -> Decimal:
        fecha_limite = datetime.now() - timedelta(days=90)
        
        result = (self.db.query(func.sum(TransactionORM.monto))
                .filter(
                    TransactionORM.user_id == user_id,
                    TransactionORM.tipo_movimiento == TipoMovimiento.EGRESO,
                    TransactionORM.tipo_gasto == TipoGasto.NECESIDAD,
                    TransactionORM.fecha >= fecha_limite
                ).scalar()) # scalar() devuelve el número directamente
        
        return result if result else Decimal(0)
    
    def get_spending_by_category(self, user_id: int, fecha_inicio: datetime, fecha_fin: datetime):
        return (self.db.query(
                    CategoryORM.nombre.label("categoria"),
                    func.sum(TransactionORM.monto).label("total")
                )
                .join(TransactionORM.category)
                .filter(
                    TransactionORM.user_id == user_id,
                    TransactionORM.tipo_movimiento == "EGRESO",
                    TransactionORM.fecha >= fecha_inicio,
                    TransactionORM.fecha <= fecha_fin
                )
                .group_by(CategoryORM.nombre)
                .all())