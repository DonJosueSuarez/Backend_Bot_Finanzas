from typing import List
from sqlalchemy.orm import Session
from app.repository.base_transaction_repository import ITransactionRepository
from app.repository.base_category_repository import ICategoryRepository
from app.dto.transaction_dtos import TransactionCreate, TransactionUpdate
from app.model.transaction import TransactionORM
from app.model.enums import TipoMovimiento, TipoGasto
from app.core.exceptions import NotFoundException


class TransactionService:

    def __init__(
        self,
        repository: ITransactionRepository,
        category_repository: ICategoryRepository,
        db: Session
    ):
        self.repository = repository
        self.category_repository = category_repository
        self.db = db

    # -------------------------
    # DTO -> ORM
    # -------------------------
    def _build_transaction(self, data: TransactionCreate) -> TransactionORM:
        values = data.model_dump(exclude={"categoria"})

        # El bot manda la categoría por nombre; se traduce a su id
        if data.categoria and values["category_id"] is None:
            category = self.category_repository.get_by_nombre(data.categoria)
            if not category:
                raise NotFoundException(f"La categoría {data.categoria.value} no existe")
            values["category_id"] = category.id

        transaction = TransactionORM(**values)
        self._apply_tipo_gasto_rules(transaction)
        return transaction

    # -------------------------
    # REGLAS DE TIPO DE GASTO
    # -------------------------
    @staticmethod
    def _apply_tipo_gasto_rules(transaction: TransactionORM) -> None:
        # Un ingreso no es necesidad ni deseo
        if transaction.tipo_movimiento == TipoMovimiento.INGRESO:
            transaction.tipo_gasto = None
        # Un egreso sin clasificar cuenta como necesidad (lo usa el KPI de supervivencia)
        elif transaction.tipo_gasto is None:
            transaction.tipo_gasto = TipoGasto.NECESIDAD

    # -------------------------
    # CREATE ONE
    # -------------------------
    def create_transaction(self, data: TransactionCreate) -> TransactionORM:
        transaction = self._build_transaction(data)

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
            self._build_transaction(t)
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

        self._apply_tipo_gasto_rules(transaction)

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