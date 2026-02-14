from pydantic import BaseModel, ConfigDict

class CategorySimple(BaseModel):
    id: int
    nombre: str # Aquí Angular ya tiene el nombre para mostrar
    color: str | None = None
    
    model_config = ConfigDict(from_attributes=True)