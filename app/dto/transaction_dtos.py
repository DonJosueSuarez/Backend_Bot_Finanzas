import unicodedata
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.model.enums import TipoMovimiento, TipoGasto, TipoCategoria
from typing import Optional
from datetime import datetime
from app.dto.user_dtos import UserSimple
from app.dto.category_dtos import CategoryResponse

class TransactionBase(BaseModel):
    # ge=0 permite registrar un saldo inicial de 0
    monto: Decimal = Field(ge=0)
    tipo_movimiento: TipoMovimiento
    descripcion: str = Field(min_length=1, max_length=255)
    category_id: Optional[int] = None
    tipo_gasto: Optional[TipoGasto] = None
    is_recurrente: bool = False

class TransactionCreate(TransactionBase):
    user_id: int
    # Alternativa a category_id para el bot: el LLM conoce nombres, no ids
    categoria: Optional[TipoCategoria] = None

    # Acepta "piqueos y comida fuera", "PIQUEOS_Y_COMIDA_FUERA" o con tildes
    @field_validator("categoria", mode="before")
    @classmethod
    def normalizar_categoria(cls, value):
        if isinstance(value, str):
            sin_tildes = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
            return sin_tildes.replace("_", " ").strip().upper() or None
        return value

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

    user: UserSimple
    category: Optional[CategoryResponse]

    model_config = ConfigDict(from_attributes=True)
