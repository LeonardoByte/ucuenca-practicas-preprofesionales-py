from abc import abstractmethod
from typing import Optional

from src.models import Administrador
from src.repositories.interfaces import RepositoryABC


class AdministradorRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_p: int) -> Optional[Administrador]: pass