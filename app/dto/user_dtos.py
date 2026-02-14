from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    nombre: str
    telegram_id: Optional[int] = None
    telefono: Optional[int] = None
    
class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True
        
class UserSimple(BaseModel):
    id: int
    nombre: str
    
    model_config = ConfigDict(from_attributes=True)