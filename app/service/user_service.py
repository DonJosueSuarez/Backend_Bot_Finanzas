from app.repository.base_user_repository import IUserRepository
from app.dto.user_dtos import UserCreate
from app.model.user import UserORM
from app.core.exceptions import NotFoundException, AppException

class UserService:
    def __init__(self, repository: IUserRepository):
        self.repository = repository
        
    def get_user_by_id(self, user_id: int) -> UserORM:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"El usuario con ID {user_id} no existe")
        return user
        
    def register_user(self, user_data: UserCreate):
        existing = self.repository.get_by_phone_number(user_data.telefono)
        if existing:
            raise AppException(f"El usuario con el teléfono {user_data.telefono} ya está registrado", status_code=400)
        
        new_user = UserORM(**user_data.model_dump())
        return self.repository.create(new_user)