from abc import abstractmethod
from typing import Optional

from src.models import Estudiante
from src.repositories.interfaces import RepositoryABC


class EstudianteRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_p: int) -> Optional[Estudiante]:
        pass

    @abstractmethod
    def buscar_por_cedula(self, cedula: str) -> Optional[Estudiante]:
        pass
