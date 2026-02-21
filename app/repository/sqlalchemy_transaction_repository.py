from typing import List
from app.model.transaction import TransactionORM
from sqlalchemy.orm import Session, joinedload
from app.repository.base_transaction_repository import ITransactionRepository
from app.dto.transaction_dtos import TransactionUpdate
from sqlalchemy import func

class PostgresTransactionRepository(ITransactionRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, transaction_id: int) -> TransactionORM:
        return self.db.query(TransactionORM).filter(TransactionORM.id == transaction_id).first()
    

    def get_by_user_id(self, user_id: int, limit: int = 10, offset: int = 0) -> List[TransactionORM]:
        return (self.db.query(TransactionORM)
                .options(
                    joinedload(TransactionORM.user),     # Carga el usuario en el mismo viaje
                    joinedload(TransactionORM.category)  # Carga la categoría en el mismo viaje
                )
                .filter(TransactionORM.user_id == user_id)
                .limit(limit)
                .offset(offset)
                .all())
    
    def delete(self, transaction: TransactionORM) -> None:
        self.db.delete(transaction)
    
    def update(self, transaction: TransactionORM) -> TransactionORM:
        return transaction
        
    
    def create(self, transaction: TransactionORM) -> TransactionORM:
        self.db.add(transaction)
        return transaction
    
    def create_many(self, transactions: List[TransactionORM]):
        self.db.add_all(transactions)
        return transactions
    
    def count_by_user_id(self, user_id: int) -> int:
        return (
            self.db.query(func.count(TransactionORM.id))
            .filter(TransactionORM.user_id == user_id)
            .scalar()
        )