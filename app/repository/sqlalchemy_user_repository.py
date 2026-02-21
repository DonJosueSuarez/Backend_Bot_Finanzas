from sqlalchemy.orm import Session
from app.repository.base_user_repository import IUserRepository
from app.model.user import UserORM
from typing import List, Optional

class PostgresUserRepository(IUserRepository):

    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, user_id: int) -> Optional[UserORM]:
        return self.db.query(UserORM).filter(UserORM.id == user_id).first()
    
    def get_by_telegram_id(self, telegram_id: str) -> Optional[UserORM]:
        return self.db.query(UserORM).filter(UserORM.telegram_id == telegram_id).first()
    
    def get_by_telefono(self, telefono: str) -> Optional[UserORM]:
        return self.db.query(UserORM).filter(UserORM.telefono == telefono).first()
        
    def create(self, user: UserORM) -> UserORM:
        self.db.add(user)
        return user
    
    def create_many(self, users: List[UserORM]) -> List[UserORM]:
        self.db.add_all(users)
        return users