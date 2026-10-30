from typing import List
from sqlalchemy.orm import Session
from app.repository.base_category_repository import ICategoryRepository
from app.model.category import CategoryORM
from app.model.enums import TipoCategoria

class CategoryService:

    def __init__(self, repository: ICategoryRepository, db: Session):
        self.repository = repository
        self.db = db

    def ensure_default_categories(self) -> List[CategoryORM]:
        """Inserta las categorías del enum que aún no existen. Se puede llamar en cada arranque."""
        existentes = {category.nombre for category in self.repository.get_all()}
        faltantes = [CategoryORM(nombre=tipo) for tipo in TipoCategoria if tipo not in existentes]

        if faltantes:
            self.repository.create_many(faltantes)
            self.db.commit()

        return faltantes
