from abc import abstractmethod
from typing import Optional

from src.models.empresa import Empresa
from src.repositories.interfaces.base_repository_abc import RepositoryABC


class EmpresaRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_e: int) -> Optional[Empresa]:
        pass
