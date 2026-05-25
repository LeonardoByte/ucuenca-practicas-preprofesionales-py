from abc import abstractmethod
from typing import Optional

from src.models import Practica
from src.repositories.interfaces import RepositoryABC


class PracticaRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_pr: int) -> Optional[Practica]:
        pass

    @abstractmethod
    def buscar_por_estudiante(self, id_p_estudiante: int) -> Optional[Practica]:
        pass
