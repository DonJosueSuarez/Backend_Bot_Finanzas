from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional
from app.dto.user_dtos import UserSimple
from app.dto.category_dtos import CategoryResponse

class BudgetBase(BaseModel):
    monto_mensual: Decimal
    category_id: Optional[int] =None
    
class BudgetCreate(BudgetBase):
    user_id: int
    
class BudgetResponse(BudgetBase):
    id: int
    user: UserSimple
    category: Optional[CategoryResponse]
    
    model_config = ConfigDict(from_attributes=True)
    
class BudgetUpdate(BaseModel):
    monto_mensual: Optional[Decimal] = None
    category_id: Optional[int] = None