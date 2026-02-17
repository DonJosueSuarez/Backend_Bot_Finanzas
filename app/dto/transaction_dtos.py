from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.model.enums import TipoMovimiento, TipoGasto
from typing import Optional
from datetime import datetime
from app.dto.user_dtos import UserSimple
from app.dto.category_dtos import CategorySimple

class TransactionBase(BaseModel):
    monto: Decimal
    tipo_movimiento: TipoMovimiento
    descripcion: str
    category_id: int
    tipo_gasto: TipoGasto
    is_recurrente: bool

class TransactionCreate(TransactionBase):
    user_id: int

class TransactionUpdate(BaseModel):
    monto: Optional[Decimal] = None
    tipo_movimiento: Optional[TipoMovimiento] = None
    descripcion: Optional[str] = None
    category_id: Optional[int] = None
    tipo_gasto: Optional[TipoGasto] = None
    is_recurrente: Optional[bool] = None

class TransactionResponse(BaseModel):
    id: int
    monto: Decimal
    tipo_movimiento: TipoMovimiento
    descripcion: str
    fecha: datetime
    tipo_gasto: Optional[TipoGasto]
    is_recurrente: bool
    
    # IMPORTANTE: Estos nombres deben ser iguales a los 'relationship' del modelo
    user: UserSimple 
    category: Optional[CategorySimple]

    model_config = ConfigDict(from_attributes=True)