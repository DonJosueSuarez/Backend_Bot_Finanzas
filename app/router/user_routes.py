from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.postgresql_connection import get_db
from app.repository.sqlalchemy_user_repository import PostgresUserRepository
from app.service.user_service import UserService
from app.dto.user_dtos import UserCreate, UserResponse

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    repository = PostgresUserRepository(db)
    service = UserService(repository)
    return service.register_user(user)