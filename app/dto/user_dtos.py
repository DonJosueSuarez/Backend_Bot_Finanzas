from pydantic import BaseModel, ConfigDict, Field, field_validator

class UserBase(BaseModel):
    nombre: str = Field(min_length=1)
    telegram_id: str = Field(min_length=1, max_length=20)
    # telefono: Optional[str] = None

    # Telegram envía el id como número; se guarda como texto
    @field_validator("telegram_id", mode="before")
    @classmethod
    def telegram_id_a_texto(cls, value):
        return str(value) if isinstance(value, int) else value

    # El first_name de Telegram admite hasta 64 caracteres y la columna solo 50
    @field_validator("nombre")
    @classmethod
    def recortar_nombre(cls, value: str) -> str:
        return value.strip()[:50]

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    tiene_saldo_inicial: bool = False

    model_config = ConfigDict(from_attributes=True)

class UserSimple(BaseModel):
    id: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)
