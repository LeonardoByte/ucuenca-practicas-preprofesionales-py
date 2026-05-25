from abc import abstractmethod
from typing import Optional

from src.models import CartaCompromiso
from src.repositories.interfaces import RepositoryABC


class CartaCompromisoRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_carta: int) -> Optional[CartaCompromiso]:
        pass

    @abstractmethod
    def buscar_por_practica(self, id_pr: int) -> Optional[CartaCompromiso]:
        pass
