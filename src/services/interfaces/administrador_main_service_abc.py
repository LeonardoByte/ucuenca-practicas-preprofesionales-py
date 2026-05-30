from abc import ABC, abstractmethod
from typing import Any, Optional

from src.models import RolUsuario


class AdministradorMainServiceABC(ABC):
    @abstractmethod
    def crear_cuenta_usuario_sistema(
        self, username_correo: str, contrasena: str, rol: RolUsuario, datos_perfil: dict
    ) -> Optional[Any]:
        """
        El Administrador es el ÚNICO con autorización para llamar a este método.
        Delega en AutenticacionService la creación del perfil humano (.dat) y la credencial.
        Retorna la entidad del perfil creado (Estudiante, Coordinador, etc.) o None si falla.
        """
        pass

    @abstractmethod
    def eliminar_usuario_sistema(self, username_correo: str) -> bool:
        """
        El Administrador es el ÚNICO con autorización para llamar a este método.
        Elimina completamente un usuario del sistema, borrando su registro
        en el archivo correspondiente (.dat) de su perfil
        y en usuarios.dat.
        Retorna True si la eliminación fue exitosa, False en caso contrario.
        """
        pass
