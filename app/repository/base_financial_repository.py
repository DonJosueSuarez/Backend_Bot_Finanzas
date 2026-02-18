from abc import ABC, abstractmethod
from typing import Dict
from decimal import Decimal
from datetime import datetime

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