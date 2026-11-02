from typing import List, Optional
from app.model.transaction import TransactionORM
from app.model.category import CategoryORM
from sqlalchemy.orm import Session, joinedload
from app.repository.base_transaction_repository import ITransactionRepository, TransactionFilters
from app.dto.transaction_dtos import TransactionUpdate
from sqlalchemy import func

class PostgresTransactionRepository(ITransactionRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, transaction_id: int) -> TransactionORM:
        return self.db.query(TransactionORM).filter(TransactionORM.id == transaction_id).first()
    

    def _filtrar(self, query, user_id: int, filters: Optional[TransactionFilters]):
        query = query.filter(TransactionORM.user_id == user_id)
        if not filters:
            return query
        if filters.fecha_inicio:
            query = query.filter(TransactionORM.fecha >= filters.fecha_inicio)
        if filters.fecha_fin:
            query = query.filter(TransactionORM.fecha < filters.fecha_fin)
        if filters.tipo_movimiento:
            query = query.filter(TransactionORM.tipo_movimiento == filters.tipo_movimiento)
        if filters.categoria:
            query = query.filter(TransactionORM.category.has(CategoryORM.nombre == filters.categoria))
        if filters.texto:
            query = query.filter(TransactionORM.descripcion.ilike(f"%{filters.texto}%"))
        return query

    def get_by_user_id(self, user_id: int, limit: int = 10, offset: int = 0, filters: Optional[TransactionFilters] = None) -> List[TransactionORM]:
        query = (self.db.query(TransactionORM)
                .options(
                    joinedload(TransactionORM.user),     # Carga el usuario en el mismo viaje
                    joinedload(TransactionORM.category)  # Carga la categoría en el mismo viaje
                ))
        return (self._filtrar(query, user_id, filters)
                .order_by(TransactionORM.fecha.desc(), TransactionORM.id.desc())
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
    
    def count_by_user_id(self, user_id: int, filters: Optional[TransactionFilters] = None) -> int:
        return self._filtrar(self.db.query(func.count(TransactionORM.id)), user_id, filters).scalar()