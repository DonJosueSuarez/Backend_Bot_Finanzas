from decimal import Decimal
from pydantic import BaseModel
from app.model.enums import TipoMovimiento
from typing import Optional

class TransactionBase(BaseModel):
    tipo: Optional[TipoMovimiento] = None
    monto: Optional[Decimal] = None
    descripcion: Optional[str] = None
    category_id: Optional[int] = None

class TransactionUpdate(TransactionBase):
    pass

class TransactionCreate(TransactionBase):
    tipo: TipoMovimiento
    monto: Decimal
    user_id: int
    category_id: int