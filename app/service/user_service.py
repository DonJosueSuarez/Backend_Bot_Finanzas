from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repository.base_user_repository import IUserRepository
from app.dto.user_dtos import UserCreate
from app.model.user import UserORM
from app.core.exceptions import NotFoundException, AppException

class UserService:

    def __init__(self, repository: IUserRepository, db: Session):
        self.repository = repository
        self.db = db
        
    def get_user_by_id(self, user_id: int) -> UserORM:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"El usuario con ID {user_id} no existe")
        return user

    def get_user_by_telegram_id(self, telegram_id: str) -> UserORM:
        user = self.repository.get_by_telegram_id(telegram_id)
        if not user:
            raise NotFoundException(f"No hay un usuario con telegram_id {telegram_id}")
        return user

    def register_user(self, user_data: UserCreate) -> UserORM:
        existing = self.repository.get_by_telegram_id(user_data.telegram_id)
        if existing:
            raise AppException(
                f"Este usuario ya está registrado",
                status_code=400
            )

        try:
            new_user = UserORM(**user_data.model_dump())
            self.repository.create(new_user)

            self.db.commit()
            self.db.refresh(new_user)

            return new_user

        except IntegrityError:
            self.db.rollback()
            raise AppException("Error de integridad en base de datos", 400)