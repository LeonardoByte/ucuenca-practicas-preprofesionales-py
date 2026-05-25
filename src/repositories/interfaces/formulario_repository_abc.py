from abc import abstractmethod
from typing import Optional

from src.models import Formulario
from src.repositories.interfaces import RepositoryABC


class FormularioRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_id(self, id_doc: int) -> Optional[Formulario]:
        pass

    @abstractmethod
    def listar_formularios_por_practica(self, id_pr: int) -> list[Formulario]:
        pass
