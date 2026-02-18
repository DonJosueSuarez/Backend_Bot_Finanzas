from app.repository.base_financial_repository import IFinancialRepository
from decimal import Decimal
import math
from typing import Optional
from datetime import datetime, date

class FinancialService:
    def __init__(self, repository: IFinancialRepository):
        self.repository = repository
        
    """     def get_balance(self, user_id: int) -> Dict[str, Decimal]:
        return self.repository.get_balance(user_id) """
            
    def get_dashboard_summary(self, user_id: int, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
        if not fecha_fin:
            fecha_fin = datetime.now()
            
        if not fecha_inicio:
            fecha_inicio = datetime.combine(date.today().replace(day=1), datetime.min.time())
            
        totals_periodo = self.repository.get_totals_by_type(user_id, fecha_inicio, fecha_fin)
        ingresos_periodo = totals_periodo.get("INGRESO", Decimal(0))
        egresos_periodo = totals_periodo.get("EGRESO", Decimal(0))
        saldo_neto = self.repository.get_total_balance_to_date(user_id, fecha_fin)
        gastos_por_categoria_raw = self.repository.get_spending_by_category(user_id, fecha_inicio, fecha_fin)
        gasto_esencial_90_dias = self.repository.get_essential_spending_last_90_days(user_id)
        diario_esencial = gasto_esencial_90_dias / 90
        
        analisis_gastos = []
        for item in gastos_por_categoria_raw:
            porcentaje = (item.total / ingresos_periodo * 100) if ingresos_periodo > 0 else 0
            
            analisis_gastos.append({
                "categoria": item.categoria,
                "monto": item.total,
                "porcentaje_sobre_ingreso": round(float(porcentaje), 2)
            })
        
        if diario_esencial > 0:
            dias_supervivencia = math.floor(float(saldo_neto / diario_esencial))
        else:
            dias_supervivencia = 999
        
        ahorro_periodo = ingresos_periodo - egresos_periodo
        tasa_ahorro = (ahorro_periodo / ingresos_periodo) if ingresos_periodo > 0 else 0
        
        return {
            "ingresos_totales": ingresos_periodo,
            "egresos_totales": egresos_periodo,
            "saldo_actual": saldo_neto,
            "tasa_ahorro": tasa_ahorro,
            "dias_supervivencia": max(0, dias_supervivencia), # Evita números negativos si hay deuda
            "desglose_por_categoria": analisis_gastos # <--- Aquí va el nuevo KPI
            #"costo_vida_diario": round(diario_esencial, 2),
            #"estado": "Saludable" if tasa_ahorro > 20 else "Ajustado"
    }