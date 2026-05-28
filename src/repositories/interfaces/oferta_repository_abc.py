from abc import abstractmethod
from typing import Optional

from src.models import Oferta
from src.repositories.interfaces.base_repository_abc import RepositoryABC


class OfertaRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_o: int) -> Optional[Oferta]:
        pass

    @abstractmethod
    def listar_por_empresa(self, id_e: int) -> list[Oferta]:
        pass
