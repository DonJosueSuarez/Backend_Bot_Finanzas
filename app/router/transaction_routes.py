from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.postgresql_connection import get_db
from app.repository.sqlalchemy_transaction_repository import PostgresTransactionRepository
from app.service.transaction_service import TransactionService
from app.dto.transaction_dtos import TransactionCreate, TransactionResponse

router = APIRouter()

@router.post("/transactions/bulk", response_model=List[TransactionResponse])
def create_many_transactions(
    transactions: List[TransactionCreate],
    db: Session = Depends(get_db)
):
    repository = PostgresTransactionRepository(db)
    service = TransactionService(repository)
    
    return service.create_many_transactions(transactions)
