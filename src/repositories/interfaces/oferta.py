from abc import abstractmethod
from typing import Optional

from src.models import Oferta
from src.repositories.interfaces.base import RepositoryABC


class OfertaRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_clave_compuesta(self, id_o: str, id_e: int) -> Optional[Oferta]:
        pass

    @abstractmethod
    def listar_ofertas_disponibles(self) -> list[Oferta]:
        pass
