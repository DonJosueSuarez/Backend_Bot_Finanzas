from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional
from app.model.enums import TipoMovimiento

from app.database.postgresql_connection import get_db
from app.repository.sqlalchemy_financial_repository import PostgresFinancialRepository
from app.service.financial_engine_service import FinancialService

router = APIRouter()

def get_financial_service(db: Session = Depends(get_db)) ->FinancialService:
    repository = PostgresFinancialRepository(db)
    return FinancialService(repository)

@router.get("/kpis")
def get_kpi(
    user_id: int,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    service: FinancialService = Depends(get_financial_service)
):
    return service.get_dashboard_summary(user_id, fecha_inicio, fecha_fin)

# Resumen de un rango de días (hora de Ecuador, ambos extremos incluidos) para el bot
@router.get("/transactions/summary")
def get_period_summary(
    user_id: int,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    tipo_movimiento: TipoMovimiento = TipoMovimiento.EGRESO,
    service: FinancialService = Depends(get_financial_service)
):
    return service.get_period_summary(user_id, fecha_desde, fecha_hasta, tipo_movimiento)

# Excel con los movimientos (hoja 1) y un dashboard (hoja 2); el bot lo envía como documento
@router.get("/transactions/export")
def export_period_excel(
    user_id: int,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    service: FinancialService = Depends(get_financial_service)
):
    nombre, contenido = service.export_period_excel(user_id, fecha_desde, fecha_hasta)
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )