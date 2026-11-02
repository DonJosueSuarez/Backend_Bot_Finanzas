from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.postgresql_connection import get_db
from app.repository.sqlalchemy_transaction_repository import PostgresTransactionRepository
from app.repository.sqlalchemy_category_repository import PostgresCategoryRepository
from app.service.transaction_service import TransactionService
from app.dto.transaction_dtos import TransactionCreate, TransactionResponse
from app.repository.base_transaction_repository import TransactionFilters
from app.model.enums import TipoMovimiento, TipoCategoria
from app.core.security import require_service, current_user_id
from app.core.fechas import inicio_dia_utc, fin_dia_utc
from pydantic import BaseModel
from typing import List

class PaginatedTransactions(BaseModel):
    data: List[TransactionResponse]
    total: int
    
router = APIRouter()

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    repository = PostgresTransactionRepository(db)
    category_repository = PostgresCategoryRepository(db)
    return TransactionService(repository, category_repository, db)

@router.post("/transactions/bulk", response_model=List[TransactionResponse], dependencies=[Depends(require_service)])
def create_many(
    transactions: List[TransactionCreate],
    service: TransactionService = Depends(get_transaction_service) # Una sola línea
):
    return service.create_many_transactions(transactions)

# Más recientes primero. Las fechas son días de Ecuador y ambos extremos se incluyen
@router.get("/transactions", response_model=PaginatedTransactions)
def get_transactions(
    user_id: int = Depends(current_user_id),
    limit: int = Query(default=10, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    tipo_movimiento: Optional[TipoMovimiento] = None,
    categoria: Optional[TipoCategoria] = None,
    q: Optional[str] = Query(default=None, max_length=100),
    service: TransactionService = Depends(get_transaction_service)
):
    filters = TransactionFilters(
        fecha_inicio=inicio_dia_utc(fecha_desde) if fecha_desde else None,
        fecha_fin=fin_dia_utc(fecha_hasta) if fecha_hasta else None,
        tipo_movimiento=tipo_movimiento,
        categoria=categoria,
        texto=q.strip() if q and q.strip() else None,
    )
    transactions = service.get_by_user_id(user_id, limit, offset, filters)
    total = service.count_by_user_id(user_id, filters)
    return {
        "data": transactions,
        "total": total
    }

@router.post("/transactions", response_model=TransactionResponse, dependencies=[Depends(require_service)])
def create_transaction(transaction: TransactionCreate, service: TransactionService = Depends(get_transaction_service)):
    return service.create_transaction(transaction)