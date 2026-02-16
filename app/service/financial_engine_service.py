from app.repository.base_financial_repository import IFinancialRepository
from typing import Dict
from decimal import Decimal

class FinancialService:
    def __init__(self, repository: IFinancialRepository):
        self.repository = repository
        
    """     def get_balance(self, user_id: int) -> Dict[str, Decimal]:
        return self.repository.get_balance(user_id) """
    
    def get_dashboard_summary(self, user_id: int):
        totals = self.repository.get_totals_by_type(user_id)
        ingresos = totals.get("INGRESO", Decimal(0))
        egresos = totals.get("EGRESO", Decimal(0))
        
        saldo_neto = ingresos - egresos
        tasa_ahorro = (saldo_neto / ingresos) if ingresos > 0 else 0
        
        return {
            "ingresos_totales": ingresos,
            "egresos_totales": egresos,
            "saldo_actual": saldo_neto,
            "tasa_ahorro": tasa_ahorro,
        }