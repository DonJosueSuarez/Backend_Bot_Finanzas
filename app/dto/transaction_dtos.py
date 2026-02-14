from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.model.enums import TipoMovimiento
from typing import Optional
from datetime import datetime
from app.dto.user_dtos import UserSimple
from app.dto.category_dtos import CategorySimple

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

class TransactionResponse(BaseModel):
    id: int
    monto: Decimal
    tipo: TipoMovimiento
    descripcion: str
    fecha: datetime
    
    # IMPORTANTE: Estos nombres deben ser iguales a los 'relationship' del modelo
    user: UserSimple 
    category: CategorySimple

    model_config = ConfigDict(from_attributes=True)