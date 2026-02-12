from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    nombre: str
    telegram_id: Optional[int] = None
    telefono: Optional[int] = None
    
class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    nombre: str
    
    class Config:
        from_attributes = True