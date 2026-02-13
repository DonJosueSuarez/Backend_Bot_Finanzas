from decimal import Decimal
from pydantic import BaseModel
from app.model.enums import TipoMovimiento
from typing import Optional

class TransactionBase(BaseModel):
    pass

class TransactionCreate(BaseModel):
    monto: Decimal
    tipo: TipoMovimiento
    descripcion: str
    user_id: int
    category_id: int

class TransactionUpdate(BaseModel):
    monto: Optional[Decimal] = None
    tipo: Optional[TipoMovimiento] = None
    descripcion: Optional[str] = None
    category_id: Optional[int] = None