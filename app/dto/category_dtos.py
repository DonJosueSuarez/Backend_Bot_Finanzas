from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.model.enums import TipoCategoria

class CategoryBase(BaseModel):
    nombre: TipoCategoria
    color: Optional[str] = None
    image: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)