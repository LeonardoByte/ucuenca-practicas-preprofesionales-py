from typing import Any, Optional

from src.services.autenticacion_service import AutenticacionService
from src.services.interfaces.administrador_main_service_abc import AdministradorMainServiceABC


class AdministradorMainService(AdministradorMainServiceABC):
    def __init__(
        self,
        autenticacion_service: Optional[AutenticacionService] = None,
    ) -> None:
        self.autenticacion_service = autenticacion_service or AutenticacionService()

    def crear_cuenta_usuario_sistema(
        self,
        username_correo: str,
        contrasena: str,
        rol: str,
        datos_perfil: dict
    ) -> Optional[Any]:
        return self.autenticacion_service.registrar_nuevo_perfil_sistema(
            username_correo=username_correo,
            contrasena=contrasena,
            rol=rol,
            datos_perfil=datos_perfil
        )

    def eliminar_usuario_sistema(self, username_correo: str) -> bool:
        return self.autenticacion_service.eliminar_cuenta_usuario_sistema(username_correo)
