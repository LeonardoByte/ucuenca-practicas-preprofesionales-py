from abc import abstractmethod
from typing import Optional

from src.models import CoordinadorDePracticas
from src.repositories.interfaces import RepositoryABC


class CoordinadorRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_p: int) -> Optional[CoordinadorDePracticas]:
        pass