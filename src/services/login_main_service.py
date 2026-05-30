from typing import Any, Optional

from src.repositories import UsuarioRepository
from src.services.autenticacion_service import AutenticacionService
from src.services.exceptions import CredencialesInvalidasError
from src.services.interfaces.login_main_service_abc import LoginMainServiceABC


class LoginMainService(LoginMainServiceABC):
    def __init__(
        self,
        autenticacion_service: Optional[AutenticacionService] = None,
        usuario_repo: Optional[UsuarioRepository] = None,
    ) -> None:
        self.autenticacion_service = autenticacion_service or AutenticacionService()
        self.usuario_repo = usuario_repo or UsuarioRepository()

    def ejecutar_ingreso(
        self, correo_electronico: str, contrasena: str
    ) -> tuple[Optional[Any], str]:
        try:
            profile = self.autenticacion_service.verificar_credenciales(
                correo_electronico, contrasena
            )
            if not profile:
                return None, ""
        except CredencialesInvalidasError:
            return None, ""

        user = self.usuario_repo.buscar_por_username(correo_electronico)
        if not user:
            return None, ""

        rol_str = user.rol.value if hasattr(user.rol, "value") else user.rol
        return profile, str(rol_str)
