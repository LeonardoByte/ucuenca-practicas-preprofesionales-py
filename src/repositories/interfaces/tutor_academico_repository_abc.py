from abc import abstractmethod
from typing import Optional

from src.models.persona import TutorAcademico
from src.repositories.interfaces import RepositoryABC


class TutorAcademicoRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_p: int) -> Optional[TutorAcademico]:
        pass