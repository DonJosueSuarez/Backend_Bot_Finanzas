from abc import ABC, abstractmethod
from typing import List, Optional
from app.model.category import CategoryORM
from app.model.enums import TipoCategoria

class ICategoryRepository(ABC):
    @abstractmethod
    def get_by_nombre(self, nombre: TipoCategoria) -> Optional[CategoryORM]:
        pass

    @abstractmethod
    def get_all(self) -> List[CategoryORM]:
        pass

    @abstractmethod
    def create_many(self, categories: List[CategoryORM]) -> List[CategoryORM]:
        pass
