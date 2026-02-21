from typing import List
from sqlalchemy.orm import Session
from app.repository.base_transaction_repository import ITransactionRepository
from app.dto.transaction_dtos import TransactionCreate, TransactionUpdate
from app.model.transaction import TransactionORM
from app.core.exceptions import NotFoundException


class TransactionService:

    def __init__(self, repository: ITransactionRepository, db: Session):
        self.repository = repository
        self.db = db

    # -------------------------
    # CREATE ONE
    # -------------------------
    def create_transaction(self, data: TransactionCreate) -> TransactionORM:
        transaction = TransactionORM(**data.model_dump())

        self.repository.create(transaction)

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    # -------------------------
    # CREATE MANY
    # -------------------------
    def create_many_transactions(
        self,
        transactions: List[TransactionCreate]
    ) -> List[TransactionORM]:

        new_transactions = [
            TransactionORM(**t.model_dump())
            for t in transactions
        ]

        self.repository.create_many(new_transactions)

        self.db.commit()

        return new_transactions

    # -------------------------
    # GET BY ID
    # -------------------------
    def get_by_id(self, transaction_id: int) -> TransactionORM:
        transaction = self.repository.get_by_id(transaction_id)

        if not transaction:
            raise NotFoundException("Transacción no encontrada")

        return transaction

    # -------------------------
    # GET BY USER
    # -------------------------
    def get_by_user_id(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[TransactionORM]:

        return self.repository.get_by_user_id(user_id, limit, offset)

    # -------------------------
    # UPDATE
    # -------------------------
    def update_transaction(
        self,
        transaction_id: int,
        data: TransactionUpdate
    ) -> TransactionORM:

        transaction = self.repository.get_by_id(transaction_id)

        if not transaction:
            raise NotFoundException("Transacción no encontrada")

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(transaction, key, value)

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    # -------------------------
    # DELETE
    # -------------------------
    def delete_transaction(self, transaction_id: int) -> None:

        transaction = self.repository.get_by_id(transaction_id)

        if not transaction:
            raise NotFoundException("Transacción no encontrada")

        self.repository.delete(transaction)

        self.db.commit()
        
    def count_by_user_id(self, user_id: int) -> int:
        return self.repository.count_by_user_id(user_id)