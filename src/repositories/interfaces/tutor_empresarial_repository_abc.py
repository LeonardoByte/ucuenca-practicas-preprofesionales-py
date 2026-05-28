from abc import abstractmethod
from typing import Optional

from src.models.persona import TutorEmpresarial
from src.repositories.interfaces.base_repository_abc import RepositoryABC


class TutorEmpresarialRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_p: int) -> Optional[TutorEmpresarial]:
        pass

    @abstractmethod
    def listar_por_empresa(self, id_e: int) -> list[TutorEmpresarial]:
        pass
