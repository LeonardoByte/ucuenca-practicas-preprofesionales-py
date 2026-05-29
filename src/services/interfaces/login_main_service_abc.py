from abc import ABC, abstractmethod
from typing import Any, Optional


class LoginMainServiceABC(ABC):
    @abstractmethod
    def ejecutar_ingreso(
        self,
        correo_electronico: str,
        contrasena: str
    ) -> tuple[Optional[Any], str]:
        """
        Valida las credenciales usando AutenticacionService.
        Retorna una tupla con la entidad del usuario autenticado (Estudiante, Empresa, etc.) y su rol (str).
        """
        pass
