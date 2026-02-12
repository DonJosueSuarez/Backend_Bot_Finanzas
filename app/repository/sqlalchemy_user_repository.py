from sqlalchemy.orm import Session
from app.repository.base_user_repository import IUserRepository
from app.model.user import UserORM

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