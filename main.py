from fastapi import FastAPI
from app.router.user_routes import router as user_router
from app.router.transaction_routes import router as transaction_router
from app.database.postgresql_connection import engine, Base
from app.model.user import UserORM
from app.model.transaction import TransactionORM
from app.model.category import CategoryORM
from global_exceptions import setup_exception_handlers
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)
setup_exception_handlers(app)
app.include_router(user_router)
app.include_router(transaction_router)