"""
Sistema de Gestión de Prácticas Preprofesionales (SGPP)

Punto de entrada principal del sistema.
"""

import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from src.controllers.router import Router
from src.models.estados import RolUsuario
from src.services.administrador_main_service import AdministradorMainService
from src.services.login_main_service import LoginMainService
from src.services.tutor_empresarial_main_service import TutorEmpresarialMainService
from src.views import LoginWindow, MainWindow_Administrador, MainWindow_TutorEmpresarial


class MainRouter(Router):
    def route_to_role(self, perfil, rol: RolUsuario) -> None:
        if rol in (RolUsuario.ADMINISTRADOR, RolUsuario.TUTOR_EMPRESARIAL):
            super().route_to_role(perfil, rol)
        else:
            QMessageBox.information(
                self.current_view,
                "Acceso Exitoso",
                f"Acceso correcto con rol: {rol.value}.\n"
                "Esta interfaz gráfica corresponde a submódulos posteriores.",
            )
            self.route_to_login()


def main():
    """Punto de entrada principal del sistema."""
    # print("Inicializando Base de Datos SGPP...")
    # inicializar_todos_los_dat_semilla()
    # print("[OK] Base de Datos SGPP inicializada correctamente.")

    app = QApplication(sys.argv)

    services = {
        "login_service": LoginMainService(),
        "administrador_service": AdministradorMainService(),
        "tutor_empresarial_service": TutorEmpresarialMainService(),
    }

    view_factories = {
        "LoginWindow": LoginWindow,
        RolUsuario.ADMINISTRADOR: MainWindow_Administrador,
        RolUsuario.TUTOR_EMPRESARIAL: MainWindow_TutorEmpresarial,
    }

    router = MainRouter(services, view_factories)
    router.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
