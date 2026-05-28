from abc import abstractmethod
from typing import Optional

from src.models import SolicitudOficio
from src.repositories.interfaces.base_repository_abc import RepositoryABC


class SolicitudOficioRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_sol_of: int) -> Optional[SolicitudOficio]:
        pass

    @abstractmethod
    def listar_por_estudiante(self, id_p_estudiante: int) -> list[SolicitudOficio]:
        pass
