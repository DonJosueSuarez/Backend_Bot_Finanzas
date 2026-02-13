from fastapi import FastAPI
from app.router.user_routes import router as user_router
from app.database.postgresql_connection import engine, Base
from app.model.user import UserORM
from app.model.transaction import TransactionORM
from app.model.category import CategoryORM

# Esta línea crea las tablas si no existen
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(user_router)