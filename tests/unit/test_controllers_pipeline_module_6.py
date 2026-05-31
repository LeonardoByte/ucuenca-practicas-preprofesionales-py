from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtWidgets import QApplication

from src.controllers import (
    AdministradorController,
    CoordinadorController,
    EmpresaController,
    EstudianteController,
    LoginController,
    Router,
    TutorAcademicoController,
    TutorEmpresarialController,
)
from src.models.estados import (
    EstadoFirmaFormulario,
    EstadoValidacionActividad,
    RolUsuario,
)
from src.services.exceptions import (
    CredencialesInvalidasError,
    DocumentacionIncompletaError,
    EvaluacionTempranaError,
    RequisitosNoCumplidosError,
)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# ==========================================
# 1. Tests para LoginController
# ==========================================

def test_login_controller_exitoso(qapp):
    mock_view = MagicMock()
    mock_view.txt_correo.text.return_value = "user@unl.edu.ec "
    mock_view.txt_contrasena.text.return_value = " secretpass "

    mock_service = MagicMock()
    dummy_profile = MagicMock()
    mock_service.ejecutar_ingreso.return_value = (dummy_profile, RolUsuario.ADMINISTRADOR)

    controller = LoginController(mock_view, mock_service)

    # Grab callback from clicked connection
    callback = mock_view.btn_login.clicked.connect.call_args[0][0]

    # Connect a spy to the signal
    spy = MagicMock()
    controller.login_exitoso.connect(spy)

    # Trigger
    callback()

    # Asserts
    mock_service.ejecutar_ingreso.assert_called_once_with("user@unl.edu.ec", "secretpass")
    spy.assert_called_once_with(dummy_profile, RolUsuario.ADMINISTRADOR)
    mock_view.mostrar_error.assert_not_called()



def test_login_controller_campos_vacios(qapp):
    mock_view = MagicMock()
    mock_view.txt_correo.text.return_value = "   "
    mock_view.txt_contrasena.text.return_value = "password"

    mock_service = MagicMock()
    controller = LoginController(mock_view, mock_service)

    callback = mock_view.btn_login.clicked.connect.call_args[0][0]
    callback()

    mock_service.ejecutar_ingreso.assert_not_called()
    mock_view.mostrar_error.assert_called_once_with("Por favor, complete todos los campos.")


def test_login_controller_credenciales_incorrectas(qapp):
    mock_view = MagicMock()
    mock_view.txt_correo.text.return_value = "wrong@unl.edu.ec"
    mock_view.txt_contrasena.text.return_value = "wrongpass"

    mock_service = MagicMock()
    mock_service.ejecutar_ingreso.return_value = (None, "")

    controller = LoginController(mock_view, mock_service)

    callback = mock_view.btn_login.clicked.connect.call_args[0][0]
    callback()

    mock_service.ejecutar_ingreso.assert_called_once_with("wrong@unl.edu.ec", "wrongpass")
    mock_view.mostrar_error.assert_called_once_with("Credenciales incorrectas.")


def test_login_controller_excepcion(qapp):
    mock_view = MagicMock()
    mock_view.txt_correo.text.return_value = "user@unl.edu.ec"
    mock_view.txt_contrasena.text.return_value = "pass"

    mock_service = MagicMock()
    mock_service.ejecutar_ingreso.side_effect = CredencialesInvalidasError("Derrumbe de aduana")

    controller = LoginController(mock_view, mock_service)

    callback = mock_view.btn_login.clicked.connect.call_args[0][0]
    callback()

    mock_view.mostrar_error.assert_called_once_with("Derrumbe de aduana")


# ==========================================
# 2. Tests para AdministradorController
# ==========================================

def test_administrador_controller_inicializacion(qapp):
    mock_view = MagicMock()
    mock_service = MagicMock()
    usuarios_dummy = [{"username_correo": "adm@test.com", "rol": RolUsuario.ADMINISTRADOR, "id_p": 1}]
    mock_service.obtener_todos_los_usuarios_sistema.return_value = usuarios_dummy

    controller = AdministradorController(mock_view, mock_service)

    mock_service.obtener_todos_los_usuarios_sistema.assert_called_once()
    mock_view.mostrar_usuarios.assert_called_once_with(usuarios_dummy)


def test_administrador_controller_crear_usuario_exito(qapp):
    mock_view = MagicMock()
    mock_view.txt_crear_correo.text.return_value = "new@unl.edu.ec"
    mock_view.txt_crear_contrasena.text.return_value = "pass123"
    mock_view.txt_crear_nombre.text.return_value = "Juan Pérez"
    mock_view.txt_crear_cedula.text.return_value = "1102938475"
    mock_view.txt_crear_direccion.text.return_value = "Loja"
    mock_view.cmb_crear_rol.currentData.return_value = RolUsuario.ESTUDIANTE

    mock_service = MagicMock()
    mock_service.crear_cuenta_usuario_sistema.return_value = MagicMock()

    controller = AdministradorController(mock_view, mock_service)

    callback = mock_view.btn_crear_usuario.clicked.connect.call_args[0][0]
    callback()

    mock_service.crear_cuenta_usuario_sistema.assert_called_once_with(
        "new@unl.edu.ec",
        "pass123",
        RolUsuario.ESTUDIANTE,
        {
            "nombre_y_apellido": "Juan Pérez",
            "cedula_dni": "1102938475",
            "direccion": "Loja",
            "nombre_empresa": "Juan Pérez",
        }
    )
    mock_view.mostrar_exito.assert_called_once_with("Usuario registrado exitosamente.")
    mock_view.limpiar_formulario_creacion.assert_called_once()
    mock_view.mostrar_seccion.assert_called_with("ver_usuarios")


def test_administrador_controller_crear_usuario_campos_vacios(qapp):
    mock_view = MagicMock()
    mock_view.txt_crear_correo.text.return_value = ""
    mock_view.txt_crear_contrasena.text.return_value = ""
    mock_view.txt_crear_nombre.text.return_value = ""

    mock_service = MagicMock()
    controller = AdministradorController(mock_view, mock_service)

    callback = mock_view.btn_crear_usuario.clicked.connect.call_args[0][0]
    callback()

    mock_service.crear_cuenta_usuario_sistema.assert_not_called()
    mock_view.mostrar_error.assert_called_once()


def test_administrador_controller_eliminar_usuario_confirmado(qapp):
    mock_view = MagicMock()
    mock_view.obtener_usuario_seleccionado.return_value = "delete@unl.edu.ec"
    mock_view.confirmar_accion.return_value = True

    mock_service = MagicMock()
    mock_service.eliminar_usuario_sistema.return_value = True

    controller = AdministradorController(mock_view, mock_service)

    callback = mock_view.btn_eliminar_usuario.clicked.connect.call_args[0][0]
    callback()

    mock_view.confirmar_accion.assert_called_once()
    mock_service.eliminar_usuario_sistema.assert_called_once_with("delete@unl.edu.ec")
    mock_view.mostrar_exito.assert_called_once()


def test_administrador_controller_eliminar_usuario_cancelado(qapp):
    mock_view = MagicMock()
    mock_view.obtener_usuario_seleccionado.return_value = "keep@unl.edu.ec"
    mock_view.confirmar_accion.return_value = False

    mock_service = MagicMock()
    controller = AdministradorController(mock_view, mock_service)

    callback = mock_view.btn_eliminar_usuario.clicked.connect.call_args[0][0]
    callback()

    mock_service.eliminar_usuario_sistema.assert_not_called()
    mock_view.mostrar_exito.assert_not_called()


# ==========================================
# 3. Tests para TutorEmpresarialController
# ==========================================

def test_tutor_empresarial_controller_inicializacion(qapp):
    mock_view = MagicMock()
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_e = 10
    tutor_perfil.id_p = 5

    empresa_dummy = MagicMock()
    mock_service.obtener_datos_empresa_tutor.return_value = empresa_dummy

    practicas_dummy = [MagicMock()]
    mock_service.obtener_practicas_tutor_emp.return_value = practicas_dummy

    controller = TutorEmpresarialController(mock_view, mock_service, tutor_perfil)

    mock_service.obtener_datos_empresa_tutor.assert_called_once_with(10)
    mock_view.mostrar_perfil_empresa.assert_called_once_with(empresa_dummy)
    mock_service.obtener_practicas_tutor_emp.assert_called_once_with(5)
    mock_view.mostrar_practicas.assert_called_once_with(practicas_dummy)


def test_tutor_empresarial_controller_proponer_actividad(qapp):
    mock_view = MagicMock()
    mock_view.obtener_practica_seleccionada.return_value = 101
    mock_view.txt_descripcion_actividad.text.return_value = "Crear API REST"

    mock_service = MagicMock()
    mock_service.proponer_actividad_practica.return_value = MagicMock()

    tutor_perfil = MagicMock()

    with patch("src.repositories.ActividadRepository") as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.listar_por_practica.return_value = []

        controller = TutorEmpresarialController(mock_view, mock_service, tutor_perfil)

        callback = mock_view.btn_proponer_actividad.clicked.connect.call_args[0][0]
        callback()

        mock_service.proponer_actividad_practica.assert_called_once_with(101, "Crear API REST")
        mock_view.mostrar_exito.assert_called_once()
        mock_view.txt_descripcion_actividad.clear.assert_called_once()
        mock_view.mostrar_actividades.assert_called_once()


def test_tutor_empresarial_controller_evaluar_f3_exito(qapp):
    mock_view = MagicMock()
    mock_view.obtener_practica_seleccionada.return_value = 101
    mock_view.obtener_estado_firma_evaluacion.return_value = EstadoFirmaFormulario.COMPLETADO
    mock_view.obtener_fecha_evaluacion.return_value = "2026-05-30"

    mock_service = MagicMock()
    mock_service.registrar_evaluacion_formulario3.return_value = True

    tutor_perfil = MagicMock()
    controller = TutorEmpresarialController(mock_view, mock_service, tutor_perfil)

    callback = mock_view.btn_evaluar_f3.clicked.connect.call_args[0][0]
    callback()

    mock_service.registrar_evaluacion_formulario3.assert_called_once_with(
        101, EstadoFirmaFormulario.COMPLETADO, "2026-05-30"
    )
    mock_view.mostrar_exito.assert_called_once()


def test_tutor_empresarial_controller_evaluar_f3_temprana(qapp):
    mock_view = MagicMock()
    mock_view.obtener_practica_seleccionada.return_value = 101
    mock_view.obtener_estado_firma_evaluacion.return_value = EstadoFirmaFormulario.COMPLETADO
    mock_view.obtener_fecha_evaluacion.return_value = "2026-05-20"

    mock_service = MagicMock()
    mock_service.registrar_evaluacion_formulario3.side_effect = EvaluacionTempranaError(
        "Faltan más de 7 días"
    )

    tutor_perfil = MagicMock()
    controller = TutorEmpresarialController(mock_view, mock_service, tutor_perfil)

    callback = mock_view.btn_evaluar_f3.clicked.connect.call_args[0][0]
    callback()

    # Should catch early evaluation error and report warning in UI
    mock_view.mostrar_advertencia.assert_called_once_with("Faltan más de 7 días")


# ==========================================
# 4. Tests para TutorAcademicoController
# ==========================================

def test_tutor_academico_controller_inicializacion(qapp):
    mock_view = MagicMock()
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_p = 12

    practicas = [MagicMock()]
    mock_service.obtener_practicas_tutor_acad.return_value = practicas

    controller = TutorAcademicoController(mock_view, mock_service, tutor_perfil)

    mock_service.obtener_practicas_tutor_acad.assert_called_once_with(12)
    mock_view.mostrar_practicas.assert_called_once_with(practicas)


def test_tutor_academico_controller_auditar_bitacora(qapp):
    mock_view = MagicMock()
    mock_view.obtener_practica_seleccionada.return_value = 202

    mock_service = MagicMock()
    actividades = [MagicMock()]
    mock_service.listar_actividades_de_practica.return_value = actividades

    tutor_perfil = MagicMock()
    controller = TutorAcademicoController(mock_view, mock_service, tutor_perfil)

    callback = mock_view.btn_auditar_bitacora.clicked.connect.call_args[0][0]
    callback()

    mock_service.listar_actividades_de_practica.assert_called_once_with(202)
    mock_view.mostrar_seccion.assert_called_with("bitacora")
    mock_view.mostrar_actividades.assert_called_once_with(actividades)


def test_tutor_academico_controller_validar_actividad(qapp):
    mock_view = MagicMock()
    mock_view.obtener_practica_seleccionada.return_value = 202
    mock_view.obtener_actividad_seleccionada.return_value = 505

    mock_service = MagicMock()
    mock_service.evaluar_actividad_alumno.return_value = True

    tutor_perfil = MagicMock()
    controller = TutorAcademicoController(mock_view, mock_service, tutor_perfil)

    callback = mock_view.btn_validar_actividad.clicked.connect.call_args[0][0]
    callback()

    mock_service.evaluar_actividad_alumno.assert_called_once_with(
        505, 202, EstadoValidacionActividad.VALIDADA
    )
    mock_view.mostrar_exito.assert_called_once()


def test_tutor_academico_controller_evaluar_f2_temprana(qapp):
    mock_view = MagicMock()
    mock_view.obtener_practica_seleccionada.return_value = 202
    mock_view.obtener_estado_firma_evaluacion.return_value = EstadoFirmaFormulario.COMPLETADO
    mock_view.obtener_fecha_evaluacion.return_value = "2026-05-15"

    mock_service = MagicMock()
    mock_service.registrar_evaluacion_formulario2.side_effect = EvaluacionTempranaError(
        "Faltan más de 7 días"
    )

    tutor_perfil = MagicMock()
    controller = TutorAcademicoController(mock_view, mock_service, tutor_perfil)

    callback = mock_view.btn_evaluar_f2.clicked.connect.call_args[0][0]
    callback()

    mock_view.mostrar_advertencia.assert_called_once_with("Faltan más de 7 días")


# ==========================================
# 5. Tests para EmpresaController
# ==========================================

def test_empresa_controller_publicar_oferta(qapp):
    mock_view = MagicMock()
    mock_view.txt_oferta_descripcion.text.return_value = "Backend dev"
    mock_view.txt_oferta_requisitos.text.return_value = "FastAPI, PostgreSQL"
    mock_view.obtener_fecha_publicacion.return_value = "2026-05-30"
    mock_view.txt_oferta_duracion.text.return_value = "3 meses"
    mock_view.txt_oferta_remuneracion.text.return_value = "650.0"

    mock_service = MagicMock()
    mock_service.registrar_oferta.return_value = MagicMock()

    empresa_perfil = MagicMock()
    empresa_perfil.id_e = 44

    controller = EmpresaController(mock_view, mock_service, empresa_perfil)

    callback = mock_view.btn_publicar_oferta.clicked.connect.call_args[0][0]
    callback()

    mock_service.registrar_oferta.assert_called_once_with(
        44, "Backend dev", "FastAPI, PostgreSQL", "2026-05-30", "3 meses", 650.0
    )
    mock_view.mostrar_exito.assert_called_once_with("Oferta publicada con éxito.")
    mock_view.txt_oferta_descripcion.clear.assert_called_once()


def test_empresa_controller_cargar_terna(qapp):
    mock_view = MagicMock()
    mock_view.obtener_oferta_seleccionada.return_value = 111

    mock_service = MagicMock()

    # Mock nested postulations and properties
    post_dummy_1 = MagicMock()
    post_dummy_1.id_o = 111
    post_dummy_1.id_terna = 99

    mock_service.postulacion_service.postulacion_repo._datos = [post_dummy_1]

    candidatos_dummy = [MagicMock(), MagicMock(), MagicMock()]
    mock_service.visualizar_terna_recibida.return_value = candidatos_dummy

    empresa_perfil = MagicMock()
    controller = EmpresaController(mock_view, mock_service, empresa_perfil)

    controller.cargar_terna_candidatos()

    mock_service.visualizar_terna_recibida.assert_called_once_with(99)
    mock_view.mostrar_candidatos.assert_called_once_with(candidatos_dummy)


def test_empresa_controller_contratar_candidato(qapp):
    mock_view = MagicMock()
    mock_view.obtener_postulacion_seleccionada.return_value = 888
    mock_view.obtener_tutor_seleccionado.return_value = 999
    mock_view.obtener_fecha_inicio.return_value = "2026-06-01"
    mock_view.obtener_fecha_fin.return_value = "2026-09-01"

    mock_service = MagicMock()
    mock_service.seleccionar_candidato_ganador.return_value = True

    empresa_perfil = MagicMock()
    controller = EmpresaController(mock_view, mock_service, empresa_perfil)

    callback = mock_view.btn_contratar_candidato.clicked.connect.call_args[0][0]
    callback()

    mock_service.seleccionar_candidato_ganador.assert_called_once_with(
        888, 999, "2026-06-01", "2026-09-01"
    )
    mock_view.mostrar_exito.assert_called_once()
    mock_view.limpiar_formulario_contratacion.assert_called_once()


# ==========================================
# 6. Tests para CoordinadorController
# ==========================================

def test_coordinador_controller_enviar_terna_invalida(qapp):
    mock_view = MagicMock()
    # Selected count != 3
    mock_view.obtener_postulaciones_terna_seleccionadas.return_value = [10, 11]

    mock_service = MagicMock()
    coordinador_perfil = MagicMock()

    controller = CoordinadorController(mock_view, mock_service, coordinador_perfil)

    callback = mock_view.btn_enviar_terna.clicked.connect.call_args[0][0]
    callback()

    mock_service.enviar_terna_a_empresa.assert_not_called()
    mock_view.mostrar_error.assert_called_once_with(
        "Debe seleccionar exactamente 3 postulaciones para enviar una terna."
    )


def test_coordinador_controller_enviar_terna_valida(qapp):
    mock_view = MagicMock()
    mock_view.obtener_postulaciones_terna_seleccionadas.return_value = [10, 11, 12]

    mock_service = MagicMock()
    mock_service.enviar_terna_a_empresa.return_value = True

    coordinador_perfil = MagicMock()
    controller = CoordinadorController(mock_view, mock_service, coordinador_perfil)

    callback = mock_view.btn_enviar_terna.clicked.connect.call_args[0][0]
    callback()

    mock_service.enviar_terna_a_empresa.assert_called_once_with([10, 11, 12])
    mock_view.mostrar_exito.assert_called_once()


def test_coordinador_controller_evaluar_autorizacion(qapp):
    mock_view = MagicMock()
    mock_view.obtener_solicitud_autorizacion_seleccionada.return_value = 77
    mock_view.txt_nombre_destinatario.text.return_value = "Carlos Cevallos"
    mock_view.txt_cargo_destinatario.text.return_value = "Rector"

    mock_service = MagicMock()
    mock_service.evaluar_solicitud_autorizacion.return_value = True

    coordinador_perfil = MagicMock()
    coordinador_perfil.id_p = 50

    controller = CoordinadorController(mock_view, mock_service, coordinador_perfil)

    callback = mock_view.btn_aprobar_autorizacion.clicked.connect.call_args[0][0]
    callback()

    mock_service.evaluar_solicitud_autorizacion.assert_called_once_with(
        77, True, 50, "Carlos Cevallos", "Rector"
    )
    mock_view.mostrar_exito.assert_called_once()
    mock_view.txt_nombre_destinatario.clear.assert_called_once()


def test_coordinador_controller_aprobar_cierre_documentacion_incompleta(qapp):
    mock_view = MagicMock()
    mock_view.obtener_practica_seleccionada.return_value = 500

    mock_service = MagicMock()
    mock_service.ejecutar_cierre_oficial_practica.side_effect = DocumentacionIncompletaError(
        "Falta firma de CC y formulario 2"
    )

    coordinador_perfil = MagicMock()
    controller = CoordinadorController(mock_view, mock_service, coordinador_perfil)

    callback = mock_view.btn_aprobar_cierre.clicked.connect.call_args[0][0]
    callback()

    mock_view.mostrar_advertencia.assert_called_once_with("Falta firma de CC y formulario 2")


# ==========================================
# 7. Tests para EstudianteController
# ==========================================

def test_estudiante_controller_catalogo(qapp):
    mock_view = MagicMock()
    mock_service = MagicMock()

    estudiante_perfil = MagicMock()
    estudiante_perfil.id_p = 33

    catalogo = [MagicMock(), MagicMock()]
    mock_service.obtener_catalogo_ofertas.return_value = catalogo

    controller = EstudianteController(mock_view, mock_service, estudiante_perfil)

    mock_service.obtener_catalogo_ofertas.assert_called_once_with(33)
    mock_view.mostrar_catalogo_ofertas.assert_called_once_with(catalogo)


def test_estudiante_controller_bitacora_bloqueada(qapp):
    mock_view = MagicMock()
    mock_service = MagicMock()
    mock_service.obtener_practica_activa_estudiante.return_value = None

    estudiante_perfil = MagicMock()
    controller = EstudianteController(mock_view, mock_service, estudiante_perfil)

    controller.ir_a_bitacora()

    mock_view.bloquear_bitacora.assert_called_with(True)
    mock_view.mostrar_advertencia.assert_called_once_with(
        "La bitácora solo es accesible para alumnos con prácticas formalizadas."
    )


def test_estudiante_controller_solicitar_postulacion_requisitos_fallidos(qapp):
    mock_view = MagicMock()
    mock_view.obtener_oferta_y_empresa_seleccionadas.return_value = (50, 44)
    mock_view.obtener_fecha_actual.return_value = "2026-05-30"

    mock_service = MagicMock()
    mock_service.solicitar_postulacion.side_effect = RequisitosNoCumplidosError(
        "No está matriculado"
    )

    estudiante_perfil = MagicMock()
    estudiante_perfil.id_p = 33

    controller = EstudianteController(mock_view, mock_service, estudiante_perfil)

    callback = mock_view.btn_aplicar_vacante.clicked.connect.call_args[0][0]
    callback()

    mock_view.mostrar_advertencia.assert_called_once_with("No está matriculado")


# ==========================================
# 8. Tests para Router Transitions
# ==========================================

def test_router_transiciones(qapp):
    mock_login_view = MagicMock()
    mock_admin_view = MagicMock()

    view_factories = {
        "LoginWindow": lambda: mock_login_view,
        RolUsuario.ADMINISTRADOR: lambda: mock_admin_view,
    }

    mock_services = {
        "login_service": MagicMock(),
        "administrador_service": MagicMock(),
    }

    router = Router(mock_services, view_factories)

    # 1. Start router -> loads login
    router.start()

    assert router.current_view == mock_login_view
    assert isinstance(router.current_controller, LoginController)
    mock_login_view.show.assert_called_once()

    # 2. Trigger login exitoso -> routes to ADMIN role window
    admin_profile = MagicMock()

    # Simulate signal emission
    router.current_controller.login_exitoso.emit(admin_profile, RolUsuario.ADMINISTRADOR)

    # Verify login view closed and cleaned
    mock_login_view.close.assert_called_once()

    assert router.current_view == mock_admin_view
    assert isinstance(router.current_controller, AdministradorController)
    mock_admin_view.show.assert_called_once()

    # 3. Trigger cerrar_sesion from admin controller -> returns to login view
    router.current_controller.cerrar_sesion.emit()

    mock_admin_view.close.assert_called_once()
    assert router.current_view == mock_login_view
    assert isinstance(router.current_controller, LoginController)
