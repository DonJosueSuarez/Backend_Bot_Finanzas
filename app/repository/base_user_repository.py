from abc import ABC, abstractmethod
from typing import Optional
from app.model.user import UserORM

class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserORM]:
        pass
    
    @abstractmethod
    def get_by_telegram_id(self, telegram_id: str) -> Optional[UserORM]:
        pass
    
    @abstractmethod
    def create(self, user: UserORM) -> UserORM:
        pass