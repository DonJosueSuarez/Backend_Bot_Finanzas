from abc import ABC, abstractmethod
from typing import Dict
from decimal import Decimal

class IFinancialRepository(ABC):
    
    @abstractmethod
    def get_totals_by_type(self, user_id: int) -> Dict[str, Decimal]:
        pass
    
    @abstractmethod
    def get_essential_spending_last_90_days(self, user_id: int) -> Decimal:
        pass