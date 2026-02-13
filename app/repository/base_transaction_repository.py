from abc import ABC, abstractmethod
from typing import List, Optional
from app.model.transaction import TransactionORM

class ITransactionRepository(ABC):
    @abstractmethod
    def get_by_id(self, transaction_id: int) -> Optional[TransactionORM]:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int, limit:int = 10, offset:int = 0) -> List[TransactionORM]:
        pass
    
    @abstractmethod
    def delete(self, transaction_id: int) -> TransactionORM:
        pass
    
    @abstractmethod
    def update(self, transaction_id: int, transaction_data: TransactionORM) -> TransactionORM:
        pass
    
    @abstractmethod
    def create(self, transaction: TransactionORM) -> bool:
        pass
    