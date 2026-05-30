from abc import ABC, abstractmethod
from typing import Any, Optional

from src.models import RolUsuario


class AutenticacionServiceABC(ABC):
    @abstractmethod
    def verificar_credenciales(self, correo_electronico: str, contrasena: str) -> Optional[Any]:
        """
        Valida el correo electrónico y la contraseña en UsuarioRepository.
        Si coincide, utiliza el rol para buscar y retornar la entidad de perfil completa
        (Estudiante, Coordinador, Tutor_Academico, Tutor_Empresarial o Empresa).
        """
        pass

    @abstractmethod
    def registrar_nuevo_perfil_sistema(
        self,
        username_correo: str,
        contrasena: str,
        rol: RolUsuario,
        datos_perfil: dict,  # diccionario con los datos del perfil
    ) -> Optional[Any]:
        """
        Orquesta el registro completo en el backend:
        1. Valida que el username_correo no exista en UsuarioRepository.
        2. Según el 'rol', empaqueta e inserta el perfil en su respectivo repositorio (.dat)
           para obtener el 'id_p' auto-generado.
        3. Crea la entidad Usuario vinculando el 'id_p' y la guarda en usuarios.dat.
        Retorna la entidad del perfil creado (Estudiante, Empresa, etc.) o None si algo falla.
        """
        pass

    @abstractmethod
    def eliminar_cuenta_usuario_sistema(self, username_correo: str) -> bool:
        """
        Elimina completamente un usuario del sistema, borrando su registro
        en el archivo correspondiente (.dat) de su perfil y en usuarios.dat.
        Retorna True si la eliminación fue exitosa, False en caso contrario.
        """
        pass
