from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.postgresql_connection import get_db
from app.repository.sqlalchemy_transaction_repository import PostgresTransactionRepository
from app.service.transaction_service import TransactionService
from app.dto.transaction_dtos import TransactionCreate, TransactionResponse

router = APIRouter()

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    repository = PostgresTransactionRepository(db)
    return TransactionService(repository)

@router.post("/transactions/bulk", response_model=List[TransactionResponse])
def create_many(
    transactions: List[TransactionCreate],
    service: TransactionService = Depends(get_transaction_service) # Una sola línea
):
    return service.create_many_transactions(transactions)

@router.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    user_id: int,
    service: TransactionService = Depends(get_transaction_service)
):
    return service.get_by_user_id(user_id)