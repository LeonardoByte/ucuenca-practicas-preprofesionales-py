from abc import abstractmethod
from typing import Optional

from src.models import SolicitudAutorizacion
from src.repositories.interfaces.base import RepositoryABC


class SolicitudAutorizacionRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_sol_aut: int) -> Optional[SolicitudAutorizacion]:
        pass

    @abstractmethod
    def listar_por_estudiante(self, id_p_estudiante: int) -> list[SolicitudAutorizacion]:
        pass
