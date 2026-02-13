from sqlalchemy.orm import Session
from app.repository.base_user_repository import IUserRepository
from app.model.user import UserORM
from typing import List

class PostgresUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, user_id: int):
        return self.db.query(UserORM).filter(UserORM.id == user_id).first()
    
    def get_by_telegram_id(self, telegram_id: str):
        return self.db.query(UserORM).filter(UserORM.telegram_id == telegram_id).first()
    
    def create(self, user: UserORM):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def create_many(self, users: List[UserORM]):
        try:
            self.db.add_all(users)
            self.db.commit()
            for user in users:
                self.db.refresh(user)
            return users
        except Exception as e:
            self.db.rollback()
            raise e
        
    