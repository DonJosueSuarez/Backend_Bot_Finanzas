from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from app.model.enums import TipoMovimiento
from app.model.transaction import TransactionORM

class IFinancialRepository(ABC):
    
    @abstractmethod
    def get_totals_by_type(self, user_id: int) -> Dict[str, Decimal]:
        pass
    
    @abstractmethod
    def get_total_balance_to_date(self, user_id: int, fecha_corte: datetime) -> Decimal:
        pass
    
    @abstractmethod
    def get_essential_spending_last_90_days(self, user_id: int) -> Decimal:
        pass

    @abstractmethod
    def get_spending_by_category(self, user_id: int, fecha_inicio: datetime, fecha_fin: datetime):
        pass

    @abstractmethod
    def get_category_breakdown(self, user_id: int, tipo_movimiento: TipoMovimiento, fecha_inicio: datetime, fecha_fin: datetime):
        pass

    @abstractmethod
    def get_totals_by_tipo_gasto(self, user_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Decimal]:
        pass

    @abstractmethod
    def get_largest_transaction(self, user_id: int, tipo_movimiento: TipoMovimiento, fecha_inicio: datetime, fecha_fin: datetime) -> Optional[TransactionORM]:
        pass

    @abstractmethod
    def get_transactions_in_period(self, user_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> List[TransactionORM]:
        pass

    @abstractmethod
    def get_latest_transactions(self, user_id: int, tipo_movimiento: TipoMovimiento, fecha_inicio: datetime, fecha_fin: datetime, limit: int) -> List[TransactionORM]:
        pass