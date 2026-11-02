from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.postgresql_connection import get_db
from app.repository.sqlalchemy_user_repository import PostgresUserRepository
from app.service.user_service import UserService
from app.dto.user_dtos import UserCreate, UserResponse
from app.core.security import require_service, current_user_id

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)):
    repository = PostgresUserRepository(db)
    return UserService(repository, db)

@router.post("/users/", response_model=UserResponse, dependencies=[Depends(require_service)])
def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    return service.register_user(user)

# Usuario de la Mini App (o el de ?user_id si llama n8n)
@router.get("/users/me", response_model=UserResponse)
def get_current_user(user_id: int = Depends(current_user_id), service: UserService = Depends(get_user_service)):
    return service.get_user_by_id(user_id)

@router.get("/users/telegram/{telegram_id}", response_model=UserResponse, dependencies=[Depends(require_service)])
def get_user_by_telegram_id(telegram_id: str, service: UserService = Depends(get_user_service)):
    return service.get_user_by_telegram_id(telegram_id)