from abc import ABC, abstractmethod
from typing import Any


class RepositoryABC(ABC):
    @abstractmethod
    def guardar(self, entidad: Any) -> bool:
        """
        Inserta una nueva entidad o actualiza una existente.
        Retorna True si la operación fue exitosa, False en caso contrario.
        """
        pass

    @abstractmethod
    def eliminar(self, id_entidad: Any) -> bool:
        """
        Purga un registro del archivo binario basándose en su ID primitivo.
        Retorna True si fue eliminado, False si no se encontró.
        """
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Any]:
        """
        Retorna una lista con todas las entidades registradas.
        """
        pass
