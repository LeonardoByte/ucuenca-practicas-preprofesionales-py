from abc import abstractmethod
from typing import Optional

from src.models.practica import Actividad
from src.repositories.interfaces import RepositoryABC

class ActividadRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_act: int) -> Optional[Actividad]:
        pass

    @abstractmethod
    def listar_por_practica(self, id_pr: int) -> list[Actividad]:
        pass