from datetime import date
from unittest.mock import MagicMock, patch, ANY
import unittest

import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox

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
    EstadoMatricula,
    EstadoConvenio,
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


def configure_mock_admin_view(mock_view):
    # Setup all required widgets on mock_view as MagicMock
    mock_view.tableWidget = MagicMock()
    mock_view.tableWidget.rowCount.return_value = 0
    mock_view.btnNavIngresarUsuario = MagicMock()
    mock_view.btnNavEliminarUsuario = MagicMock()
    mock_view.btnNavCerrarSesion = MagicMock()
    mock_view.actRegistrarUsuario = MagicMock()
    mock_view.actAuditoriaUsuarios = MagicMock()
    mock_view.actCerrarSesion = MagicMock()
    mock_view.actSalirSistema = MagicMock()
    mock_view.actAcercaPrograma = MagicMock()
    mock_view.actAcercaDesarrollador = MagicMock()
    mock_view.actRepositorioGithub = MagicMock()
    mock_view.btnCrearUsuario = MagicMock()
    mock_view.btnEliminarUsuario = MagicMock()
    mock_view.cmbTipoUsuario = MagicMock()
    mock_view.txtBusquedaCorreo = MagicMock()
    mock_view.txtBusquedaCorreo.text.return_value = ""
    mock_view.stackedWidgetCentral = MagicMock()
    mock_view.stackedWidgetFormularios = MagicMock()
    mock_view.cmbTutorEmpEmpresa = MagicMock()
    mock_view.cmbTutorEmpEmpresa.count.return_value = 0
    
    # Estudiante inputs
    mock_view.txtEstudianteNombre = MagicMock()
    mock_view.txtEstudianteNombre.text.return_value = ""
    mock_view.txtEstudianteCedula = MagicMock()
    mock_view.txtEstudianteCedula.text.return_value = ""
    mock_view.txtEstudianteCorreo = MagicMock()
    mock_view.txtEstudianteCorreo.text.return_value = ""
    mock_view.txtEstudianteDireccion = MagicMock()
    mock_view.txtEstudianteDireccion.text.return_value = ""
    mock_view.sbxEstudianteCiclo = MagicMock()
    mock_view.sbxEstudianteCiclo.value.return_value = 1
    mock_view.comboBox = MagicMock()
    
    # Personal inputs
    mock_view.txtPersonalNombre = MagicMock()
    mock_view.txtPersonalNombre.text.return_value = ""
    mock_view.txtPersonalCedula = MagicMock()
    mock_view.txtPersonalCedula.text.return_value = ""
    mock_view.txtPersonalCorreo = MagicMock()
    mock_view.txtPersonalCorreo.text.return_value = ""
    mock_view.txtPersonalDireccion = MagicMock()
    mock_view.txtPersonalDireccion.text.return_value = ""
    
    # Tutor Empresarial inputs
    mock_view.txtTutorEmpNombre = MagicMock()
    mock_view.txtTutorEmpNombre.text.return_value = ""
    mock_view.txtTutorEmpCedula = MagicMock()
    mock_view.txtTutorEmpCedula.text.return_value = ""
    mock_view.txtTutorEmpCorreo = MagicMock()
    mock_view.txtTutorEmpCorreo.text.return_value = ""
    mock_view.txtTutorEmpDireccion = MagicMock()
    mock_view.txtTutorEmpDireccion.text.return_value = ""
    
    # Empresa inputs
    mock_view.txtEmpresaNombre = MagicMock()
    mock_view.txtEmpresaNombre.text.return_value = ""
    mock_view.txtEmpresaCorreo = MagicMock()
    mock_view.txtEmpresaCorreo.text.return_value = ""
    mock_view.comboBox_2 = MagicMock()



# ==========================================
# 1. Tests para LoginController
# ==========================================

def test_login_controller_exitoso(qapp):
    mock_view = MagicMock()
    mock_view.txtCorreo = mock_view.txt_correo
    mock_view.txtContrasena = mock_view.txt_contrasena
    mock_view.btnIngresar = mock_view.btn_login
    mock_view.txt_correo.text.return_value = "user@unl.edu.ec "
    mock_view.txt_contrasena.text.return_value = " secretpass "

    mock_service = MagicMock()
    dummy_profile = MagicMock()
    mock_service.ejecutar_ingreso.return_value = (dummy_profile, RolUsuario.ADMINISTRADOR)

    with patch("src.controllers.login_controller.uic.loadUi"):
        controller = LoginController(mock_view, mock_service)

    # Grab callback from clicked connection
    callback = mock_view.btnIngresar.clicked.connect.call_args[0][0]

    # Connect a spy to the signal
    spy = MagicMock()
    controller.login_exitoso.connect(spy)

    # Trigger
    callback()

    # Asserts
    mock_service.ejecutar_ingreso.assert_called_once_with("user@unl.edu.ec", "secretpass")
    spy.assert_called_once_with(dummy_profile, RolUsuario.ADMINISTRADOR)


def test_login_controller_campos_vacios(qapp):
    mock_view = MagicMock()
    mock_view.txtCorreo = mock_view.txt_correo
    mock_view.txtContrasena = mock_view.txt_contrasena
    mock_view.btnIngresar = mock_view.btn_login
    mock_view.txt_correo.text.return_value = "   "
    mock_view.txt_contrasena.text.return_value = "password"

    mock_service = MagicMock()
    with patch("src.controllers.login_controller.uic.loadUi"), \
         patch("src.controllers.login_controller.QMessageBox.critical") as mock_critical:
        controller = LoginController(mock_view, mock_service)

        callback = mock_view.btnIngresar.clicked.connect.call_args[0][0]
        callback()

    mock_service.ejecutar_ingreso.assert_not_called()
    mock_critical.assert_called_once_with(mock_view, "Error de Validación", "Debe ingresar el correo electrónico.")


def test_login_controller_credenciales_incorrectas(qapp):
    mock_view = MagicMock()
    mock_view.txtCorreo = mock_view.txt_correo
    mock_view.txtContrasena = mock_view.txt_contrasena
    mock_view.btnIngresar = mock_view.btn_login
    mock_view.txt_correo.text.return_value = "wrong@unl.edu.ec"
    mock_view.txt_contrasena.text.return_value = "wrongpass"

    mock_service = MagicMock()
    mock_service.ejecutar_ingreso.return_value = (None, "")

    with patch("src.controllers.login_controller.uic.loadUi"), \
         patch("src.controllers.login_controller.QMessageBox.critical") as mock_critical:
        controller = LoginController(mock_view, mock_service)

        callback = mock_view.btnIngresar.clicked.connect.call_args[0][0]
        callback()

    mock_service.ejecutar_ingreso.assert_called_once_with("wrong@unl.edu.ec", "wrongpass")
    mock_critical.assert_called_once_with(mock_view, "Error de Acceso", "Credenciales incorrectas.")


def test_login_controller_excepcion(qapp):
    mock_view = MagicMock()
    mock_view.txtCorreo = mock_view.txt_correo
    mock_view.txtContrasena = mock_view.txt_contrasena
    mock_view.btnIngresar = mock_view.btn_login
    mock_view.txt_correo.text.return_value = "user@unl.edu.ec"
    mock_view.txt_contrasena.text.return_value = "pass"

    mock_service = MagicMock()
    mock_service.ejecutar_ingreso.side_effect = CredencialesInvalidasError("Derrumbe de aduana")

    with patch("src.controllers.login_controller.uic.loadUi"), \
         patch("src.controllers.login_controller.QMessageBox.critical") as mock_critical:
        controller = LoginController(mock_view, mock_service)

        callback = mock_view.btnIngresar.clicked.connect.call_args[0][0]
        callback()

    mock_critical.assert_called_once_with(mock_view, "Error de Acceso", "Derrumbe de aduana")


# ==========================================
# 2. Tests para AdministradorController
# ==========================================

def test_administrador_controller_inicializacion(qapp):
    mock_view = MagicMock()
    configure_mock_admin_view(mock_view)
    mock_service = MagicMock()
    usuarios_dummy = [{"username_correo": "adm@test.com", "rol": RolUsuario.ADMINISTRADOR, "id_p": 1}]
    mock_service.obtener_todos_los_usuarios_sistema.return_value = usuarios_dummy

    with patch("src.controllers.administrador_controller.uic.loadUi"):
        controller = AdministradorController(mock_view, mock_service)

    mock_service.obtener_todos_los_usuarios_sistema.assert_called_once()
    mock_view.tableWidget.setRowCount.assert_called_once_with(0)
    mock_view.tableWidget.insertRow.assert_called_once_with(0)
    mock_view.tableWidget.setItem.assert_any_call(0, 0, ANY)


def test_administrador_controller_crear_usuario_exito(qapp):
    mock_view = MagicMock()
    configure_mock_admin_view(mock_view)
    mock_view.cmbTipoUsuario.currentIndex.return_value = 0
    mock_view.txtEstudianteCorreo.text.return_value = "new@unl.edu.ec"
    mock_view.txtEstudianteNombre.text.return_value = "Juan Pérez"
    mock_view.txtEstudianteCedula.text.return_value = "1102938475"
    mock_view.txtEstudianteDireccion.text.return_value = "Loja"
    mock_view.sbxEstudianteCiclo.value.return_value = 5
    mock_view.comboBox.currentText.return_value = "Matriculado"

    mock_service = MagicMock()
    mock_service.crear_cuenta_usuario_sistema.return_value = MagicMock()

    with patch("src.controllers.administrador_controller.uic.loadUi"), \
         patch("src.controllers.administrador_controller.QMessageBox.information") as mock_info:
        controller = AdministradorController(mock_view, mock_service)

        callback = mock_view.btnCrearUsuario.clicked.connect.call_args[0][0]
        callback()

    mock_service.crear_cuenta_usuario_sistema.assert_called_once_with(
        "new@unl.edu.ec",
        "password",
        RolUsuario.ESTUDIANTE,
        {
            "nombre_y_apellido": "Juan Pérez",
            "cedula_dni": "1102938475",
            "direccion": "Loja",
            "ciclo_actual": 5,
            "estado_de_matricula": EstadoMatricula.MATRICULADO,
        }
    )
    mock_info.assert_called_once_with(mock_view, "Registro exitoso", "La información fue guardada correctamente.")
    mock_view.txtEstudianteNombre.clear.assert_called_once()


def test_administrador_controller_crear_usuario_campos_vacios(qapp):
    mock_view = MagicMock()
    configure_mock_admin_view(mock_view)
    mock_view.cmbTipoUsuario.currentIndex.return_value = 0
    mock_view.txtEstudianteCorreo.text.return_value = ""
    mock_view.txtEstudianteNombre.text.return_value = ""
    mock_view.txtEstudianteCedula.text.return_value = ""

    mock_service = MagicMock()
    with patch("src.controllers.administrador_controller.uic.loadUi"), \
         patch("src.controllers.administrador_controller.QMessageBox.critical") as mock_critical:
        controller = AdministradorController(mock_view, mock_service)

        callback = mock_view.btnCrearUsuario.clicked.connect.call_args[0][0]
        callback()

    mock_service.crear_cuenta_usuario_sistema.assert_not_called()
    mock_critical.assert_called_once()


def test_administrador_controller_eliminar_usuario_confirmado(qapp):
    mock_view = MagicMock()
    configure_mock_admin_view(mock_view)
    mock_item = MagicMock()
    mock_item.row.return_value = 0
    mock_view.tableWidget.selectedItems.return_value = [mock_item]
    mock_correo_item = MagicMock()
    mock_correo_item.text.return_value = "delete@unl.edu.ec"
    mock_view.tableWidget.item.return_value = mock_correo_item

    mock_service = MagicMock()
    mock_service.eliminar_usuario_sistema.return_value = True

    with patch("src.controllers.administrador_controller.uic.loadUi"), \
         patch("src.controllers.administrador_controller.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes), \
         patch("src.controllers.administrador_controller.QMessageBox.information") as mock_info:
        controller = AdministradorController(mock_view, mock_service)

        callback = mock_view.btnEliminarUsuario.clicked.connect.call_args[0][0]
        callback()

    mock_service.eliminar_usuario_sistema.assert_called_once_with("delete@unl.edu.ec")
    mock_info.assert_called_once_with(mock_view, "Baja exitosa", "El usuario fue eliminado correctamente.")


def test_administrador_controller_eliminar_usuario_cancelado(qapp):
    mock_view = MagicMock()
    configure_mock_admin_view(mock_view)
    mock_item = MagicMock()
    mock_item.row.return_value = 0
    mock_view.tableWidget.selectedItems.return_value = [mock_item]
    mock_correo_item = MagicMock()
    mock_correo_item.text.return_value = "keep@unl.edu.ec"
    mock_view.tableWidget.item.return_value = mock_correo_item

    mock_service = MagicMock()

    with patch("src.controllers.administrador_controller.uic.loadUi"), \
         patch("src.controllers.administrador_controller.QMessageBox.question", return_value=QMessageBox.StandardButton.No), \
         patch("src.controllers.administrador_controller.QMessageBox.information") as mock_info:
        controller = AdministradorController(mock_view, mock_service)

        callback = mock_view.btnEliminarUsuario.clicked.connect.call_args[0][0]
        callback()

    mock_service.eliminar_usuario_sistema.assert_not_called()
    mock_info.assert_not_called()



# ==========================================
# 3. Tests para TutorEmpresarialController
# ==========================================

def configure_mock_tutor_view(mock_view):
    mock_view.btnNavPracticantes = MagicMock()
    mock_view.btnNavEmpresa = MagicMock()
    mock_view.btnNavCerrarSesion = MagicMock()
    mock_view.actVerPracticantes = MagicMock()
    mock_view.actVerEmpresa = MagicMock()
    mock_view.actCerrarSesion = MagicMock()
    mock_view.actSalirSistema = MagicMock()
    mock_view.actAcercaPrograma = MagicMock()
    mock_view.actAcercaDesarrollador = MagicMock()
    mock_view.actRepositorioGithub = MagicMock()
    mock_view.actProponerActividad = MagicMock()
    mock_view.btnVerBitacora = MagicMock()
    mock_view.btnEvaluarFormulario3 = MagicMock()
    mock_view.btnProponerActividad = MagicMock()
    mock_view.txtBusquedaAlumno = MagicMock()
    mock_view.stackedWidgetCentral = MagicMock()
    mock_view.txtNombre = MagicMock()
    mock_view.txtCorreoElectronico = MagicMock()
    mock_view.txtContactoPrincipal = MagicMock()
    mock_view.txtDireccionMatriz = MagicMock()
    mock_view.txtEstadoConvenio = MagicMock()
    
    tblPracticas = MagicMock()
    tblPracticas.rowCount.return_value = 0
    tblPracticas.selectedItems.return_value = []
    mock_view.tblPracticas = tblPracticas
    
    mock_view.tblBitacora = MagicMock()
    mock_view.txaDescripcionActividad = MagicMock()


def test_tutor_empresarial_controller_inicializacion(qapp):
    mock_view = MagicMock()
    configure_mock_tutor_view(mock_view)
    
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_e = 10
    tutor_perfil.id_p = 5

    empresa_dummy = MagicMock()
    empresa_dummy.nombre_empresa = "Empresa Test"
    empresa_dummy.correo_electronico = "contacto@test.com"
    empresa_dummy.numeros_contacto = ["1234567"]
    empresa_dummy.direcciones = ["Calle Falsa 123"]
    empresa_dummy.estado_de_convenio_emp.value = "ACTIVO"
    mock_service.obtener_datos_empresa_tutor.return_value = empresa_dummy

    mock_service.obtener_practicas_tutor_emp.return_value = []

    with patch("src.controllers.tutor_empresarial_controller.uic.loadUi"):
        controller = TutorEmpresarialController(mock_view, mock_service, tutor_perfil)

    mock_service.obtener_datos_empresa_tutor.assert_called_once_with(10)
    mock_view.txtNombreEmpresa.setText.assert_called_once_with("Empresa Test")
    mock_view.txtCorreoElectronicoEmpresa.setText.assert_called_once_with("contacto@test.com")
    mock_service.obtener_practicas_tutor_emp.assert_called_once_with(5)


def test_tutor_empresarial_controller_proponer_actividad(qapp):
    mock_view = MagicMock()
    configure_mock_tutor_view(mock_view)
    
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_e = 10
    tutor_perfil.id_p = 5
    
    mock_service.obtener_datos_empresa_tutor.return_value = None
    mock_service.obtener_practicas_tutor_emp.return_value = []

    # Mock selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblPracticas.selectedItems.return_value = [selected_item]
    
    table_item = MagicMock()
    table_item.data.return_value = 101
    mock_view.tblPracticas.item.return_value = table_item
    
    # Input text
    mock_view.txaDescripcionActividad.text.return_value = "Crear API REST"
    
    mock_service.proponer_actividad_practica.return_value = MagicMock()

    with patch("src.controllers.tutor_empresarial_controller.uic.loadUi"), \
         patch("src.controllers.tutor_empresarial_controller.QMessageBox.information") as mock_info, \
         patch("src.repositories.ActividadRepository") as mock_repo_class:
        
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.listar_por_practica.return_value = []
        
        controller = TutorEmpresarialController(mock_view, mock_service, tutor_perfil)
        
        # Trigger the slot connected to btnProponerActividad.clicked
        callback = mock_view.btnProponerActividad.clicked.connect.call_args[0][0]
        callback()

    mock_service.proponer_actividad_practica.assert_called_once_with(101, "Crear API REST")
    mock_info.assert_called_once_with(
        mock_view, "Actividad Registrada", "La actividad fue guardada correctamente."
    )
    mock_view.txaDescripcionActividad.clear.assert_called_once()


def test_tutor_empresarial_controller_evaluar_f3_exito(qapp):
    mock_view = MagicMock()
    configure_mock_tutor_view(mock_view)
    
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_e = 10
    tutor_perfil.id_p = 5
    
    mock_service.obtener_datos_empresa_tutor.return_value = None
    mock_service.obtener_practicas_tutor_emp.return_value = []

    # Mock selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblPracticas.selectedItems.return_value = [selected_item]
    
    table_item = MagicMock()
    table_item.data.return_value = 101
    mock_view.tblPracticas.item.return_value = table_item
    
    mock_service.registrar_evaluacion_formulario3.return_value = True

    with patch("src.controllers.tutor_empresarial_controller.uic.loadUi"), \
         patch("src.controllers.tutor_empresarial_controller.QMessageBox.information") as mock_info:
        
        controller = TutorEmpresarialController(mock_view, mock_service, tutor_perfil)
        
        callback = mock_view.btnEvaluarFormulario3.clicked.connect.call_args[0][0]
        callback()

    mock_service.registrar_evaluacion_formulario3.assert_called_once_with(
        101, EstadoFirmaFormulario.COMPLETADO, date.today().strftime("%Y-%m-%d")
    )
    mock_info.assert_called_once_with(
        mock_view, "Evaluación Guardada", "La información fue guardada correctamente."
    )


def test_tutor_empresarial_controller_evaluar_f3_temprana(qapp):
    mock_view = MagicMock()
    configure_mock_tutor_view(mock_view)
    
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_e = 10
    tutor_perfil.id_p = 5
    
    mock_service.obtener_datos_empresa_tutor.return_value = None
    mock_service.obtener_practicas_tutor_emp.return_value = []

    # Mock selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblPracticas.selectedItems.return_value = [selected_item]
    
    table_item = MagicMock()
    table_item.data.return_value = 101
    mock_view.tblPracticas.item.return_value = table_item
    
    mock_service.registrar_evaluacion_formulario3.side_effect = EvaluacionTempranaError(
        "Faltan más de 7 días"
    )

    with patch("src.controllers.tutor_empresarial_controller.uic.loadUi"), \
         patch("src.controllers.tutor_empresarial_controller.QMessageBox.warning") as mock_warning:
        
        controller = TutorEmpresarialController(mock_view, mock_service, tutor_perfil)
        
        callback = mock_view.btnEvaluarFormulario3.clicked.connect.call_args[0][0]
        callback()

    mock_warning.assert_called_once_with(mock_view, "Evaluación Anticipada", "Faltan más de 7 días")


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

    mock_login_view.btnIngresar = mock_login_view.btn_login
    mock_login_view.txtCorreo = mock_login_view.txt_correo
    mock_login_view.txtContrasena = mock_login_view.txt_contrasena
    
    configure_mock_admin_view(mock_admin_view)

    view_factories = {
        "LoginWindow": lambda: mock_login_view,
        RolUsuario.ADMINISTRADOR: lambda: mock_admin_view,
    }

    mock_services = {
        "login_service": MagicMock(),
        "administrador_service": MagicMock(),
    }

    with patch("src.controllers.login_controller.uic.loadUi"), \
         patch("src.controllers.administrador_controller.uic.loadUi"):
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

