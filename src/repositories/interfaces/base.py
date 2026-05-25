from abc import ABC, abstractmethod
from typing import Any


class RepositoryABC(ABC):
    @abstractmethod
    def guardar(self, entidad: Any) -> bool:
        pass

    @abstractmethod
    def eliminar(self, id_entidad: Any) -> bool:
        pass
