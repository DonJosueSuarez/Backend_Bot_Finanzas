from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from app.model.transaction import TransactionORM
from app.model.enums import TipoMovimiento, TipoCategoria


@dataclass
class TransactionFilters:
    """Filtros opcionales del listado; las fechas ya vienen en UTC."""
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    tipo_movimiento: Optional[TipoMovimiento] = None
    categoria: Optional[TipoCategoria] = None
    texto: Optional[str] = None


class ITransactionRepository(ABC):
    @abstractmethod
    def get_by_id(self, transaction_id: int) -> Optional[TransactionORM]:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int, limit:int = 10, offset:int = 0, filters: Optional[TransactionFilters] = None) -> List[TransactionORM]:
        pass
    
    @abstractmethod
    def delete(self, transaction: TransactionORM) -> None:
        pass
    
    @abstractmethod
    def update(self, transaction_data: TransactionORM) -> TransactionORM:
        pass
    
    @abstractmethod
    def create(self, transaction: TransactionORM) -> TransactionORM:
        pass
    
    @abstractmethod
    def create_many(self, transactions: List[TransactionORM]) -> List[TransactionORM]:
        pass
    
    @abstractmethod
    def count_by_user_id(self, user_id: int, filters: Optional[TransactionFilters] = None) -> int:
        pass