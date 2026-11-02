from sqlalchemy import func
from decimal import Decimal
from app.model.transaction import TransactionORM
from app.model.category import CategoryORM
from app.model.enums import TipoMovimiento, TipoGasto
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from app.repository.base_financial_repository import IFinancialRepository
from typing import Dict, List, Optional

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
                        TransactionORM.fecha < fecha_fin)
                .group_by(TransactionORM.tipo_movimiento)
                .all())
        
        totals = {"INGRESO": Decimal(0), "EGRESO": Decimal(0)}
        
        for r in result:
            totals[r.tipo_movimiento.value] = r.total
            
        return totals
    
    def get_total_balance_to_date(self, user_id: int, fecha_fin: datetime) -> Decimal:
        """Calcula el saldo acumulado desde el inicio de los tiempos hasta la fecha_fin."""
        ingresos = (self.db.query(func.sum(TransactionORM.monto))
                    .filter(
                        TransactionORM.user_id == user_id,
                        TransactionORM.tipo_movimiento == TipoMovimiento.INGRESO,
                        TransactionORM.fecha < fecha_fin
                    ).scalar()) or Decimal(0)
                    
        egresos = (self.db.query(func.sum(TransactionORM.monto))
                .filter(
                    TransactionORM.user_id == user_id,
                    TransactionORM.tipo_movimiento == TipoMovimiento.EGRESO,
                    TransactionORM.fecha < fecha_fin
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
                    TransactionORM.tipo_movimiento == TipoMovimiento.EGRESO,
                    TransactionORM.fecha >= fecha_inicio,
                    TransactionORM.fecha < fecha_fin
                )
                .group_by(CategoryORM.nombre)
                .all())

    def _period_filter(self, query, user_id: int, tipo_movimiento: TipoMovimiento, fecha_inicio: datetime, fecha_fin: datetime):
        return query.filter(
            TransactionORM.user_id == user_id,
            TransactionORM.tipo_movimiento == tipo_movimiento,
            TransactionORM.fecha >= fecha_inicio,
            TransactionORM.fecha < fecha_fin
        )

    def get_category_breakdown(self, user_id: int, tipo_movimiento: TipoMovimiento, fecha_inicio: datetime, fecha_fin: datetime):
        # outerjoin: los ingresos suelen no tener categoría y también deben sumar
        query = (self.db.query(
                    CategoryORM.nombre.label("categoria"),
                    func.sum(TransactionORM.monto).label("total"),
                    func.count(TransactionORM.id).label("cantidad")
                )
                .select_from(TransactionORM)
                .outerjoin(TransactionORM.category))
        return (self._period_filter(query, user_id, tipo_movimiento, fecha_inicio, fecha_fin)
                .group_by(CategoryORM.nombre)
                .order_by(func.sum(TransactionORM.monto).desc())
                .all())

    def get_totals_by_tipo_gasto(self, user_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Decimal]:
        query = self.db.query(
            TransactionORM.tipo_gasto,
            func.sum(TransactionORM.monto).label("total")
        )
        result = (self._period_filter(query, user_id, TipoMovimiento.EGRESO, fecha_inicio, fecha_fin)
                  .group_by(TransactionORM.tipo_gasto)
                  .all())

        totals = {t.value: Decimal(0) for t in TipoGasto}
        for r in result:
            if r.tipo_gasto:
                totals[r.tipo_gasto.value] = r.total
        return totals

    def get_largest_transaction(self, user_id: int, tipo_movimiento: TipoMovimiento, fecha_inicio: datetime, fecha_fin: datetime) -> Optional[TransactionORM]:
        query = self.db.query(TransactionORM).options(joinedload(TransactionORM.category))
        return (self._period_filter(query, user_id, tipo_movimiento, fecha_inicio, fecha_fin)
                .order_by(TransactionORM.monto.desc())
                .first())

    def get_transactions_in_period(self, user_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> List[TransactionORM]:
        # Ingresos y egresos juntos, en orden cronológico (para el Excel)
        return (self.db.query(TransactionORM)
                .options(joinedload(TransactionORM.category))
                .filter(
                    TransactionORM.user_id == user_id,
                    TransactionORM.fecha >= fecha_inicio,
                    TransactionORM.fecha < fecha_fin
                )
                .order_by(TransactionORM.fecha, TransactionORM.id)
                .all())

    def get_latest_transactions(self, user_id: int, tipo_movimiento: TipoMovimiento, fecha_inicio: datetime, fecha_fin: datetime, limit: int) -> List[TransactionORM]:
        query = self.db.query(TransactionORM).options(joinedload(TransactionORM.category))
        return (self._period_filter(query, user_id, tipo_movimiento, fecha_inicio, fecha_fin)
                .order_by(TransactionORM.fecha.desc())
                .limit(limit)
                .all())