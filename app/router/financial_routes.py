from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
    service: FinancialService = Depends(get_financial_service)
):
    return service.get_dashboard_summary(user_id)