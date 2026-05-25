from abc import abstractmethod
from typing import Optional

from src.models.empresa import Convenio
from src.repositories.interfaces import RepositoryABC


class ConvenioRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_con: int) -> Optional[Convenio]:
        pass

    @abstractmethod
    def buscar_por_empresa(self, id_e: int) -> Optional[Convenio]:
        pass