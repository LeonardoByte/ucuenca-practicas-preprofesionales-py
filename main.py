"""
Sistema de Gestión de Prácticas Preprofesionales (SGPP)

Punto de entrada principal del sistema.
"""

import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from src.controllers.router import Router
from src.models.estados import RolUsuario
from src.services.administrador_main_service import AdministradorMainService
from src.services.coordinador_main_service import CoordinadorMainService
from src.services.empresa_main_service import EmpresaMainService
from src.services.login_main_service import LoginMainService
from src.services.tutor_academico_main_service import TutorAcademicoMainService
from src.services.tutor_empresarial_main_service import TutorEmpresarialMainService
from src.views import (
    LoginWindow,
    MainWindow_Administrador,
    MainWindow_Coordinador,
    MainWindow_Empresa,
    MainWindow_TutorAcademico,
    MainWindow_TutorEmpresarial,
)


class MainRouter(Router):
    def route_to_role(self, perfil, rol: RolUsuario) -> None:
        if rol in (
            RolUsuario.ADMINISTRADOR,
            RolUsuario.TUTOR_EMPRESARIAL,
            RolUsuario.TUTOR_ACADEMICO,
            RolUsuario.EMPRESARIO,
            RolUsuario.COORDINADOR,
        ):
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
        "tutor_academico_service": TutorAcademicoMainService(),
        "empresa_service": EmpresaMainService(),
        "coordinador_service": CoordinadorMainService(),
    }

    view_factories = {
        "LoginWindow": LoginWindow,
        RolUsuario.ADMINISTRADOR: MainWindow_Administrador,
        RolUsuario.TUTOR_EMPRESARIAL: MainWindow_TutorEmpresarial,
        RolUsuario.TUTOR_ACADEMICO: MainWindow_TutorAcademico,
        RolUsuario.EMPRESARIO: MainWindow_Empresa,
        RolUsuario.COORDINADOR: MainWindow_Coordinador,
    }

    router = MainRouter(services, view_factories)
    router.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
