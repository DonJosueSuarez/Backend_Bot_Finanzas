from app.repository.base_financial_repository import IFinancialRepository
from decimal import Decimal
import math

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
        
        gasto_esencial_90_dias = self.repository.get_essential_spending_last_90_days(user_id)
        diario_esencial = gasto_esencial_90_dias / 90
        
        if diario_esencial > 0:
            dias_supervivencia = math.floor(float(saldo_neto / diario_esencial))
        else:
            dias_supervivencia = 999
        
        tasa_ahorro = (saldo_neto / ingresos) if ingresos > 0 else 0
        
        return {
            "ingresos_totales": ingresos,
            "egresos_totales": egresos,
            "saldo_actual": saldo_neto,
            "tasa_ahorro": tasa_ahorro,
            "dias_supervivencia": max(0, dias_supervivencia), # Evita números negativos si hay deuda
            #"costo_vida_diario": round(diario_esencial, 2),
            #"estado": "Saludable" if tasa_ahorro > 20 else "Ajustado"
    }