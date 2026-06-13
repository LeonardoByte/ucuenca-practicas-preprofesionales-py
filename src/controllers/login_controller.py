import re

from PyQt6 import uic
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from src.models.estados import RolUsuario
from src.services.exceptions import CredencialesInvalidasError
from src.services.interfaces.login_main_service_abc import LoginMainServiceABC


class LoginController(QObject):
    login_exitoso = pyqtSignal(object, RolUsuario)

    def __init__(self, view, service: LoginMainServiceABC) -> None:
        super().__init__()
        self.view = view
        self.service = service

        # Load the dynamic UI
        uic.loadUi("src/views/ui/frm_login.ui", self.view)

        # Apply global QSS style to buttons
        from src.utils.qss_loader import aplicar_qss_global
        aplicar_qss_global(self.view)

        # Connect signals
        self.view.btnIngresar.clicked.connect(self.procesar_login)

    def procesar_login(self) -> None:
        correo = self.view.txtCorreo.text().strip()
        contrasena = self.view.txtContrasena.text().strip()

        if not correo:
            QMessageBox.critical(
                self.view, "Error de Validación", "Debe ingresar el correo electrónico."
            )
            return


        if not contrasena:
            QMessageBox.critical(self.view, "Error de Validación", "Debe ingresar la contraseña.")
            return

        # Validate email format
        patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(patron, correo):
            QMessageBox.critical(
                self.view,
                "Error de Validación",
                "El correo electrónico no tiene un formato válido."
            )
            return

        try:
            profile, rol = self.service.ejecutar_ingreso(correo, contrasena)
            if profile is None or not rol:
                QMessageBox.critical(self.view, "Error de Acceso", "Credenciales incorrectas.")
                return

            if isinstance(rol, str):
                rol = RolUsuario(rol)

            self.login_exitoso.emit(profile, rol)
        except CredencialesInvalidasError as e:
            QMessageBox.critical(self.view, "Error de Acceso", str(e))
        except Exception as e:
            QMessageBox.critical(self.view, "Error Inesperado", f"Error inesperado: {str(e)}")

