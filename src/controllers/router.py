from PyQt6.QtCore import QObject

from src.models.estados import RolUsuario


class Router(QObject):
    def __init__(self, services, view_factories=None) -> None:
        super().__init__()
        self.services = services
        self.view_factories = view_factories or {}
        self.current_view = None
        self.current_controller = None

    def start(self) -> None:
        self.route_to_login()

    def route_to_login(self) -> None:
        self._clear_current()

        login_view_class = self.view_factories.get("LoginWindow")
        if not login_view_class:
            return

        self.current_view = login_view_class()

        from src.controllers.login_controller import LoginController

        self.current_controller = LoginController(
            self.current_view, self.services.get("login_service")
        )
        self.current_controller.login_exitoso.connect(self.route_to_role)
        self.current_view.show()

    def route_to_role(self, perfil, rol: RolUsuario) -> None:
        self._clear_current()

        view_class = self.view_factories.get(rol)
        if not view_class:
            return

        self.current_view = view_class()

        # Instantiate correct controller based on role
        if rol == RolUsuario.ADMINISTRADOR:
            from src.controllers.administrador_controller import AdministradorController

            self.current_controller = AdministradorController(
                self.current_view, self.services.get("administrador_service")
            )
        elif rol == RolUsuario.ESTUDIANTE:
            from src.controllers.estudiante_controller import EstudianteController

            self.current_controller = EstudianteController(
                self.current_view, self.services.get("estudiante_service"), perfil
            )
        elif rol == RolUsuario.TUTOR_ACADEMICO:
            from src.controllers.tutor_academico_controller import TutorAcademicoController

            self.current_controller = TutorAcademicoController(
                self.current_view, self.services.get("tutor_academico_service"), perfil
            )
        elif rol == RolUsuario.TUTOR_EMPRESARIAL:
            from src.controllers.tutor_empresarial_controller import (
                TutorEmpresarialController,
            )

            self.current_controller = TutorEmpresarialController(
                self.current_view, self.services.get("tutor_empresarial_service"), perfil
            )
        elif rol == RolUsuario.EMPRESARIO:
            from src.controllers.empresa_controller import EmpresaController

            self.current_controller = EmpresaController(
                self.current_view, self.services.get("empresa_service"), perfil
            )
        elif rol == RolUsuario.COORDINADOR:
            from src.controllers.coordinador_controller import CoordinadorController

            self.current_controller = CoordinadorController(
                self.current_view, self.services.get("coordinador_service"), perfil
            )

        if self.current_controller:
            self.current_controller.cerrar_sesion.connect(self.route_to_login)

        self.current_view.show()

    def _clear_current(self) -> None:
        if self.current_view:
            self.current_view.close()
            self.current_view = None
        self.current_controller = None
