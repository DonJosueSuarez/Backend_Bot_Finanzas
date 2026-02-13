from typing import List
from app.model.transaction import TransactionORM
from sqlalchemy.orm import Session
from app.repository.base_transaction_repository import ITransactionRepository
from app.dto.transaction_dtos import TransactionUpdate

class PostgresUserRepository(ITransactionRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, transaction_id: int):
        return self.db.query(TransactionORM).filter(TransactionORM.id == transaction_id).first()
    
    def get_by_user_id(self, user_id, limit = 10, offset = 0):
        return (self.db.query(TransactionORM)
                .filter(TransactionORM.user_id == user_id)
                .limit(limit)
                .offset(offset)
                .all())
    
    def delete(self, transaction_id):
        transaction = self.db.query(TransactionORM).filter(TransactionORM.id == transaction_id).first()
        if transaction:
            self.db.delete(transaction)
            self.db.commit()
            return True
        return False
    
    def update(self, transaction_id, transaction_data: TransactionUpdate):
        db_transaction = self.get_by_id(transaction_id)
        if not db_transaction:
            return None
        update_data = transaction_data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_transaction, key, value)
            
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction
        
    
    def create(self, transaction):
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def create_many(self, transactions: List[TransactionORM]):
        try:
            self.db.add_all(transactions)
            self.db.commit()
            for transaction in transactions:
                self.db.refresh(transaction)
            return transactions
        except Exception as e:
            self.db.rollback()
            raise e