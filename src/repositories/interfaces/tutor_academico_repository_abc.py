from abc import abstractmethod
from typing import Optional

from src.models.persona import TutorAcademico
from src.repositories.interfaces.base_repository_abc import RepositoryABC


class TutorAcademicoRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_p: int) -> Optional[TutorAcademico]:
        pass
