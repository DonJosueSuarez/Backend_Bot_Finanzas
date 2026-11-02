from app.repository.base_financial_repository import IFinancialRepository
from decimal import Decimal
import math
from typing import Optional
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from app.model.enums import TipoMovimiento
from app.core.exceptions import AppException
from app.report.excel_report import build_excel_report

LOCAL_TZ = ZoneInfo("America/Guayaquil")
# El bot lista los movimientos solo si caben en un mensaje de Telegram
MAX_MOVIMIENTOS = 20

class FinancialService:
    def __init__(self, repository: IFinancialRepository):
        self.repository = repository

    @staticmethod
    def _rango(fecha_desde: Optional[date], fecha_hasta: Optional[date]):
        hoy = datetime.now(LOCAL_TZ).date()
        fecha_desde = fecha_desde or hoy.replace(day=1)
        fecha_hasta = fecha_hasta or hoy
        if fecha_desde > fecha_hasta:
            raise AppException("fecha_desde no puede ser posterior a fecha_hasta")

        # Días completos en hora local: [desde 00:00, hasta + 1 día 00:00)
        inicio = datetime.combine(fecha_desde, time.min, LOCAL_TZ).astimezone(ZoneInfo("UTC"))
        fin = datetime.combine(fecha_hasta + timedelta(days=1), time.min, LOCAL_TZ).astimezone(ZoneInfo("UTC"))
        return fecha_desde, fecha_hasta, inicio, fin

    def export_period_excel(
        self,
        user_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ):
        fecha_desde, fecha_hasta, inicio, fin = self._rango(fecha_desde, fecha_hasta)
        movimientos = [
            {
                "fecha": t.fecha.astimezone(LOCAL_TZ).date(),
                "tipo_movimiento": t.tipo_movimiento.value,
                "descripcion": t.descripcion,
                "categoria": t.category.nombre.value if t.category else None,
                "tipo_gasto": t.tipo_gasto.value if t.tipo_gasto else None,
                "monto": t.monto,
            }
            for t in self.repository.get_transactions_in_period(user_id, inicio, fin)
        ]
        contenido = build_excel_report(movimientos, fecha_desde, fecha_hasta, datetime.now(LOCAL_TZ))
        return f"reporte_{fecha_desde}_{fecha_hasta}.xlsx", contenido

    def get_period_summary(
        self,
        user_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        tipo_movimiento: TipoMovimiento = TipoMovimiento.EGRESO
    ):
        fecha_desde, fecha_hasta, inicio, fin = self._rango(fecha_desde, fecha_hasta)

        categorias = self.repository.get_category_breakdown(user_id, tipo_movimiento, inicio, fin)
        mayor = self.repository.get_largest_transaction(user_id, tipo_movimiento, inicio, fin)
        ultimos = self.repository.get_latest_transactions(user_id, tipo_movimiento, inicio, fin, MAX_MOVIMIENTOS)

        def movimiento(t):
            return {
                "fecha": t.fecha.astimezone(LOCAL_TZ).date(),
                "descripcion": t.descripcion,
                "monto": t.monto,
                "categoria": t.category.nombre.value if t.category else None,
            }

        return {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "tipo_movimiento": tipo_movimiento,
            "total": sum((c.total for c in categorias), Decimal(0)),
            "cantidad": sum(c.cantidad for c in categorias),
            "por_categoria": [
                {
                    "categoria": c.categoria.value if c.categoria else None,
                    "total": c.total,
                    "cantidad": c.cantidad,
                }
                for c in categorias
            ],
            # Necesidad/deseo solo existe en egresos
            "por_tipo_gasto": (
                self.repository.get_totals_by_tipo_gasto(user_id, inicio, fin)
                if tipo_movimiento == TipoMovimiento.EGRESO else None
            ),
            "mayor": movimiento(mayor) if mayor else None,
            "movimientos": [movimiento(t) for t in ultimos],
        }
        
    """     def get_balance(self, user_id: int) -> Dict[str, Decimal]:
        return self.repository.get_balance(user_id) """
            
    def get_dashboard_summary(self, user_id: int, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
        local_tz = ZoneInfo("America/Guayaquil")
        now_local = datetime.now(local_tz)
        if not fecha_inicio:
            fecha_inicio = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if not fecha_fin:
            fecha_fin = now_local

        # Convertimos a UTC antes de enviar al repository
        fecha_inicio = fecha_inicio.astimezone(ZoneInfo("UTC"))
        fecha_fin = fecha_fin.astimezone(ZoneInfo("UTC"))
            
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