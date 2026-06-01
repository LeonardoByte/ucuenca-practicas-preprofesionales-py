from PyQt6.QtCore import QObject

from src.controllers.administrador_controller import AdministradorController
from src.controllers.coordinador_controller import CoordinadorController
from src.controllers.empresa_controller import EmpresaController
from src.controllers.estudiante_controller import EstudianteController
from src.controllers.login_controller import LoginController
from src.controllers.tutor_academico_controller import TutorAcademicoController
from src.controllers.tutor_empresarial_controller import (
    TutorEmpresarialController,
)
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
        match rol:
            case RolUsuario.ADMINISTRADOR:
                self.current_controller = AdministradorController(
                    self.current_view, self.services.get("administrador_service")
                )
            case RolUsuario.ESTUDIANTE:
                self.current_controller = EstudianteController(
                    self.current_view, self.services.get("estudiante_service"), perfil
                )
            case RolUsuario.TUTOR_ACADEMICO:
                self.current_controller = TutorAcademicoController(
                    self.current_view, self.services.get("tutor_academico_service"), perfil
                )
            case RolUsuario.TUTOR_EMPRESARIAL:
                self.current_controller = TutorEmpresarialController(
                    self.current_view, self.services.get("tutor_empresarial_service"), perfil
                )
            case RolUsuario.EMPRESARIO:
                self.current_controller = EmpresaController(
                    self.current_view, self.services.get("empresa_service"), perfil
                )
            case RolUsuario.COORDINADOR:
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
