from abc import abstractmethod
from typing import Optional

from src.models.usuario import Usuario
from src.repositories.interfaces import RepositoryABC


class UsuarioRepositoryABC(RepositoryABC):
    @abstractmethod
    def buscar_por_username(self, username_correo: str) -> Optional[Usuario]:
        pass