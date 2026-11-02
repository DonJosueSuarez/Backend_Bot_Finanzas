from fastapi import FastAPI, Depends
from app.router.user_routes import router as user_router
from app.router.transaction_routes import router as transaction_router
from app.router.financial_routes import router as financial_router
from app.database.postgresql_connection import engine, Base, SessionLocal
from app.model.user import UserORM
from app.model.transaction import TransactionORM
from app.model.category import CategoryORM
from app.model.budget import BudgetORM
from app.repository.sqlalchemy_category_repository import PostgresCategoryRepository
from app.service.category_service import CategoryService
from app.core.security import authenticate
from app.core.config import Config
from global_exceptions import setup_exception_handlers
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

# Las transacciones del bot se clasifican por nombre de categoría, así que deben existir
with SessionLocal() as db:
    CategoryService(PostgresCategoryRepository(db), db).ensure_default_categories()

app = FastAPI(dependencies=[Depends(authenticate)])
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
setup_exception_handlers(app)
app.include_router(user_router)
app.include_router(transaction_router)
app.include_router(financial_router)