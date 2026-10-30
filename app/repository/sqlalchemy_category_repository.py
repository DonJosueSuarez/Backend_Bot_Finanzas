from typing import List, Optional
from sqlalchemy.orm import Session
from app.model.category import CategoryORM
from app.model.enums import TipoCategoria
from app.repository.base_category_repository import ICategoryRepository

class PostgresCategoryRepository(ICategoryRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_nombre(self, nombre: TipoCategoria) -> Optional[CategoryORM]:
        return self.db.query(CategoryORM).filter(CategoryORM.nombre == nombre).first()

    def get_all(self) -> List[CategoryORM]:
        return self.db.query(CategoryORM).all()

    def create_many(self, categories: List[CategoryORM]) -> List[CategoryORM]:
        self.db.add_all(categories)
        return categories
