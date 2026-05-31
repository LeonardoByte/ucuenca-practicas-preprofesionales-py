from PyQt6.QtCore import QObject, pyqtSignal

from src.models.estados import RolUsuario
from src.services.exceptions import CredencialesInvalidasError
from src.services.interfaces.login_main_service_abc import LoginMainServiceABC


class LoginController(QObject):
    login_exitoso = pyqtSignal(object, RolUsuario)

    def __init__(self, view, service: LoginMainServiceABC) -> None:
        super().__init__()
        self.view = view
        self.service = service
        self.view.btn_login.clicked.connect(self.procesar_login)

    def procesar_login(self) -> None:
        correo = self.view.txt_correo.text().strip()
        contrasena = self.view.txt_contrasena.text().strip()

        if not correo or not contrasena:
            self.view.mostrar_error("Por favor, complete todos los campos.")
            return

        try:
            profile, rol = self.service.ejecutar_ingreso(correo, contrasena)
            if profile is None or not rol:
                self.view.mostrar_error("Credenciales incorrectas.")
                return

            # Cast role if it is a string representation, or keep enum
            if isinstance(rol, str):
                rol = RolUsuario(rol)

            self.login_exitoso.emit(profile, rol)
        except CredencialesInvalidasError as e:
            self.view.mostrar_error(str(e))
        except Exception as e:
            self.view.mostrar_error(f"Error inesperado: {str(e)}")
