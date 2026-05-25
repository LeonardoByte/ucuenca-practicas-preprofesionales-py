from abc import ABC, abstractmethod
from typing import Optional, Any


class AutenticacionServiceABC(ABC):
    @abstractmethod
    def verificar_credenciales(self, correo_electronico: str, contrasena: str) -> Optional[Any]:
        """
        Valida el correo electrónico y la contraseña en UsuarioRepository.
        Si coincide, utiliza el rol para buscar y retornar la entidad de perfil completa
        (Estudiante, Coordinador, Tutor_Academico, Tutor_Empresarial o Empresa).
        """
        pass