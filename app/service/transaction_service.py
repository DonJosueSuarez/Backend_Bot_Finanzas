from typing import List
from app.repository.base_transaction_repository import ITransactionRepository
from app.dto.transaction_dtos import TransactionCreate
from app.model.transaction import TransactionORM
class TransactionService:
    def __init__(self, repository: ITransactionRepository):
        self.repository = repository
        
    def create_many_transactions(self, transactions: List[TransactionCreate]):
        new_transactions = [
            TransactionORM(**t.model_dump()) 
            for t in transactions
        ]
        return self.repository.create_many(new_transactions)
    
    def get_by_user_id(self, user_id: int, limit: int = 10, offset: int = 0) -> List[TransactionORM]:
        return self.repository.get_by_user_id(user_id, limit, offset)