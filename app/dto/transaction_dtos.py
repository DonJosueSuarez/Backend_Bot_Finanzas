from decimal import Decimal
from pydantic import BaseModel
from app.model.enums import TipoMovimiento
from typing import Optional

class TransactionBase(BaseModel):
    monto: Decimal
    tipo: TipoMovimiento
    descripcion: str
    category_id: int

class TransactionCreate(TransactionBase):
    user_id: int

class TransactionUpdate(BaseModel):
    monto: Optional[Decimal] = None
    tipo: Optional[TipoMovimiento] = None
    descripcion: Optional[str] = None
    category_id: Optional[int] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
