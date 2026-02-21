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
        
    def register_user(self, user_data: UserCreate) -> UserORM:
        existing = self.repository.get_by_telefono(user_data.telefono)
        if existing:
            raise AppException(
                f"El usuario con el teléfono {user_data.telefono} ya está registrado",
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