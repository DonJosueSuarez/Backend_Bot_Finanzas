from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.postgresql_connection import get_db
from app.repository.sqlalchemy_transaction_repository import PostgresTransactionRepository
from app.service.transaction_service import TransactionService
from app.dto.transaction_dtos import TransactionCreate, TransactionResponse
from pydantic import BaseModel
from typing import List

class PaginatedTransactions(BaseModel):
    data: List[TransactionResponse]
    total: int
    
router = APIRouter()

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    repository = PostgresTransactionRepository(db)
    return TransactionService(repository, db)

@router.post("/transactions/bulk", response_model=List[TransactionResponse])
def create_many(
    transactions: List[TransactionCreate],
    service: TransactionService = Depends(get_transaction_service) # Una sola línea
):
    return service.create_many_transactions(transactions)

@router.get("/transactions", response_model=PaginatedTransactions)
def get_transactions(
    user_id: int,
    limit: int = 10,
    offset: int = 0,
    service: TransactionService = Depends(get_transaction_service)
):
    transactions = service.get_by_user_id(user_id, limit, offset)
    total = service.count_by_user_id(user_id)
    return {
        "data": transactions,
        "total": total
    }

@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, service: TransactionService = Depends(get_transaction_service)):
    return service.create_transaction(transaction)