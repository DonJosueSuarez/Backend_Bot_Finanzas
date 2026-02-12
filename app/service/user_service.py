from app.repository.base_user_repository import IUserRepository
from app.dto.user_dtos import UserCreate
from app.model.user import UserORM

class UserService:
    def __init__(self, repository: IUserRepository):
        self.repository = repository
        
    def register_user(self, user_data: UserCreate):
        new_user = UserORM(
            nombre = user_data.nombre,
            telegram_id = user_data.telegram_id,
            telefono = user_data.telefono
        )
        return self.repository.create(new_user)