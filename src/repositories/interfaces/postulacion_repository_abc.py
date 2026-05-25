from abc import abstractmethod
from typing import Optional

from src.models import Postulacion
from src.repositories.interfaces import RepositoryABC


class PostulacionRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_pos: int) -> Optional[Postulacion]:
        pass

    @abstractmethod
    def listar_por_estudiante(self, id_p_estudiante: int) -> list[Postulacion]:
        pass

    @abstractmethod
    def listar_por_oferta_compuesta(self, id_o: str, id_e: int) -> list[Postulacion]:
        pass

    @abstractmethod
    def listar_por_id_terna(self, id_terna: int) -> list[Postulacion]:
        pass
