from datetime import date
import json
from unittest.mock import ANY, MagicMock, patch

import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox, QComboBox, QDialog, QLineEdit

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
    EstadoMatricula,
    EstadoValidacionActividad,
    RolUsuario,
    EstadoPostulacion,
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

def configure_mock_acad_view(mock_view):
    mock_view.btnNavEstudiantes = MagicMock()
    mock_view.btnNavBitacora = MagicMock()
    mock_view.btnNavCerrarSesion = MagicMock()
    mock_view.pushButton = MagicMock()
    mock_view.pushButton_2 = MagicMock()
    mock_view.pushButton_3 = MagicMock()

    mock_view.actVerEstudiantes = MagicMock()
    mock_view.actAuditarBitacora = MagicMock()
    mock_view.actCerrarSesion = MagicMock()
    mock_view.actSalirSistema = MagicMock()
    mock_view.actAcercaPrograma = MagicMock()
    mock_view.actAcercaDesarrollador = MagicMock()
    mock_view.actRepositorioGithub = MagicMock()

    mock_view.btnAuditarBitacora = MagicMock()
    mock_view.btnEvaluarFormulario2 = MagicMock()
    mock_view.btnValidarActividad = MagicMock()
    mock_view.btnRechazarActividad = MagicMock()

    mock_view.txtBusquedaEstudiante = MagicMock()
    mock_view.stackedWidgetCentral = MagicMock()

    tblEstudiantes = MagicMock()
    tblEstudiantes.rowCount.return_value = 0
    tblEstudiantes.selectedItems.return_value = []
    mock_view.tblEstudiantes = tblEstudiantes

    mock_view.tblBitacoraAuditoria = MagicMock()


def test_tutor_academico_controller_inicializacion(qapp):
    mock_view = MagicMock()
    configure_mock_acad_view(mock_view)
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_p = 12

    mock_service.obtener_practicas_tutor_acad.return_value = []

    with patch("src.controllers.tutor_academico_controller.uic.loadUi"):
        controller = TutorAcademicoController(mock_view, mock_service, tutor_perfil)

    mock_service.obtener_practicas_tutor_acad.assert_called_once_with(12)


def test_tutor_academico_controller_auditar_bitacora(qapp):
    mock_view = MagicMock()
    configure_mock_acad_view(mock_view)
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_p = 12

    mock_service.obtener_practicas_tutor_acad.return_value = []

    # Mock selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblEstudiantes.selectedItems.return_value = [selected_item]

    table_item = MagicMock()
    table_item.data.return_value = 202
    mock_view.tblEstudiantes.item.return_value = table_item

    mock_service.listar_actividades_de_practica.return_value = []

    with patch("src.controllers.tutor_academico_controller.uic.loadUi"):
        controller = TutorAcademicoController(mock_view, mock_service, tutor_perfil)

        callback = mock_view.btnAuditarBitacora.clicked.connect.call_args[0][0]
        callback()

    mock_service.listar_actividades_de_practica.assert_called_once_with(202)
    mock_view.stackedWidgetCentral.setCurrentIndex.assert_called_with(1)


def test_tutor_academico_controller_validar_actividad(qapp):
    mock_view = MagicMock()
    configure_mock_acad_view(mock_view)
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_p = 12

    mock_service.obtener_practicas_tutor_acad.return_value = []

    # Mock practice selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblEstudiantes.selectedItems.return_value = [selected_item]

    table_item = MagicMock()
    table_item.data.return_value = 202
    mock_view.tblEstudiantes.item.return_value = table_item

    # Mock activity selection
    selected_act_item = MagicMock()
    selected_act_item.row.return_value = 0
    mock_view.tblBitacoraAuditoria.selectedItems.return_value = [selected_act_item]

    table_act_item = MagicMock()
    table_act_item.data.return_value = 505
    mock_view.tblBitacoraAuditoria.item.return_value = table_act_item

    mock_service.evaluar_actividad_alumno.return_value = True

    with patch("src.controllers.tutor_academico_controller.uic.loadUi"), \
         patch("src.controllers.tutor_academico_controller.QMessageBox.information") as mock_info:
        controller = TutorAcademicoController(mock_view, mock_service, tutor_perfil)

        callback = mock_view.btnValidarActividad.clicked.connect.call_args[0][0]
        callback()

    mock_service.evaluar_actividad_alumno.assert_called_once_with(
        505, 202, EstadoValidacionActividad.VALIDADA
    )
    mock_info.assert_called_once()


def test_tutor_academico_controller_evaluar_f2_temprana(qapp):
    mock_view = MagicMock()
    configure_mock_acad_view(mock_view)
    mock_service = MagicMock()
    tutor_perfil = MagicMock()
    tutor_perfil.id_p = 12

    # Mock practice selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblEstudiantes.selectedItems.return_value = [selected_item]

    table_item = MagicMock()
    table_item.data.return_value = 202
    mock_view.tblEstudiantes.item.return_value = table_item

    practica = MagicMock()
    practica.fecha_fin = "2026-06-15"
    mock_service.practica_service.practica_repo.buscar_por_id.return_value = practica
    mock_service.obtener_practicas_tutor_acad.return_value = []

    with patch("src.controllers.tutor_academico_controller.uic.loadUi"), \
         patch("src.controllers.tutor_academico_controller.QMessageBox.warning") as mock_warning:
        controller = TutorAcademicoController(mock_view, mock_service, tutor_perfil)

        callback = mock_view.btnEvaluarFormulario2.clicked.connect.call_args[0][0]
        callback()

    mock_warning.assert_called_once()
    mock_view.btnEvaluarFormulario2.setEnabled.assert_called_with(False)



# ==========================================
# 5. Tests para EmpresaController
# ==========================================

def configure_mock_empresa_view(mock_view):
    mock_view.txtTituloOferta = MagicMock()
    mock_view.txtDescripcionOferta = MagicMock()
    mock_view.txaRequisitos = MagicMock()
    mock_view.txtDuracionOferta = MagicMock()
    mock_view.dspnRemuneracion = MagicMock()
    mock_view.btnPublicar = MagicMock()
    mock_view.btnVerTerna = MagicMock()
    mock_view.btnVolverHistorial = MagicMock()
    mock_view.btnAceptarPostulacion = MagicMock()
    mock_view.btnRechazarPostulacion = MagicMock()
    mock_view.txtFiltradoOferta = MagicMock()
    mock_view.txtBusquedaTutor = MagicMock()
    mock_view.tblOfertasHistorico = MagicMock()
    mock_view.tableWidget = MagicMock()
    mock_view.tblPostulantesTerna = MagicMock()
    mock_view.stackedWidgetCentral = MagicMock()
    mock_view.actAcercaPrograma = MagicMock()
    mock_view.actAcercaDesarrollador = MagicMock()
    mock_view.actRepositorioGithub = MagicMock()


def test_empresa_controller_publicar_oferta(qapp):
    mock_view = MagicMock()
    configure_mock_empresa_view(mock_view)
    mock_view.txtTituloOferta.text.return_value = "Backend dev"
    mock_view.txaRequisitos.text.return_value = "FastAPI, PostgreSQL"
    mock_view.txtDescripcionOferta.text.return_value = "Python Developer"
    mock_view.txtDuracionOferta.text.return_value = "3 meses"
    mock_view.dspnRemuneracion.value.return_value = 650.0

    mock_service = MagicMock()
    mock_service.registrar_oferta.return_value = MagicMock()
    mock_service.listar_mis_ofertas_publicadas.return_value = []
    mock_service.obtener_tutores_de_empresa.return_value = []

    empresa_perfil = MagicMock()
    empresa_perfil.id_e = 44

    with patch("src.controllers.empresa_controller.uic.loadUi"):
        controller = EmpresaController(mock_view, mock_service, empresa_perfil)

    with patch("src.controllers.empresa_controller.QMessageBox.information") as mock_info:
        controller.publicar_oferta()
        mock_info.assert_called_once()
        expected_json = json.dumps({"titulo": "Backend dev", "descripcion": "Python Developer"})
        mock_service.registrar_oferta.assert_called_once_with(
            44,
            expected_json,
            "FastAPI, PostgreSQL",
            date.today().strftime("%Y-%m-%d"),
            "3 meses",
            650.0,
        )


def test_empresa_controller_cargar_terna(qapp):
    mock_view = MagicMock()
    configure_mock_empresa_view(mock_view)

    mock_service = MagicMock()
    mock_service.listar_mis_ofertas_publicadas.return_value = []
    mock_service.obtener_tutores_de_empresa.return_value = []

    # Mock selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblOfertasHistorico.selectedItems.return_value = [selected_item]

    table_item = MagicMock()
    table_item.data.return_value = 111
    mock_view.tblOfertasHistorico.item.return_value = table_item

    # Mock nested postulations and properties
    post_dummy_1 = MagicMock()
    post_dummy_1.id_o = 111
    post_dummy_1.id_terna = 99
    post_dummy_1.id_p_estudiante = 201

    mock_service.postulacion_service.repo._datos = [post_dummy_1]

    candidatos_dummy = [post_dummy_1]
    mock_service.visualizar_terna_recibida.return_value = candidatos_dummy

    est = MagicMock(cedula_dni="1722", nombre_y_apellido="Est", correo_electronico="est@unl.edu.ec")
    mock_service.practica_service.estudiante_repo.buscar_por_id.return_value = est

    empresa_perfil = MagicMock()
    with patch("src.controllers.empresa_controller.uic.loadUi"):
        controller = EmpresaController(mock_view, mock_service, empresa_perfil)

    controller.cargar_terna(111)

    mock_service.visualizar_terna_recibida.assert_called_once_with(99)
    assert mock_view.tblPostulantesTerna.insertRow.call_count == 1


def test_empresa_controller_contratar_candidato(qapp):
    mock_view = MagicMock()
    configure_mock_empresa_view(mock_view)

    # Mock selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblPostulantesTerna.selectedItems.return_value = [selected_item]

    table_item = MagicMock()
    table_item.data.return_value = 888
    mock_view.tblPostulantesTerna.item.return_value = table_item

    mock_service = MagicMock()
    mock_service.listar_mis_ofertas_publicadas.return_value = []
    mock_service.obtener_tutores_de_empresa.return_value = []
    mock_service.seleccionar_candidato_ganador.return_value = True

    empresa_perfil = MagicMock()
    with patch("src.controllers.empresa_controller.uic.loadUi"):
        controller = EmpresaController(mock_view, mock_service, empresa_perfil)

    def mock_dialog_exec(self):
        combos = self.findChildren(QComboBox)
        line_edits = self.findChildren(QLineEdit)
        if combos:
            combos[0].setCurrentIndex(0)
        if len(line_edits) >= 2:
            line_edits[0].setText("2026-06-01")
            line_edits[1].setText("2026-09-01")
        return QDialog.DialogCode.Accepted

    with patch("src.controllers.empresa_controller.QDialog.exec", mock_dialog_exec), \
         patch("src.controllers.empresa_controller.QMessageBox.information") as mock_info:
        # Mocking tutor selection combo
        tutor = MagicMock(id_p=999)
        tutor.nombre_y_apellido = "Tutor Name"
        mock_service.obtener_tutores_de_empresa.return_value = [tutor]
        controller.aceptar_postulacion()
        mock_service.seleccionar_candidato_ganador.assert_called_once_with(
            888, 999, "2026-06-01", "2026-09-01"
        )
        mock_info.assert_called_once()


# ==========================================
# 6. Tests para CoordinadorController
# ==========================================

def configure_mock_coordinador_view(mock_view):
    mock_view.btnNavPostulaciones = MagicMock()
    mock_view.btnNavAsignaciones = MagicMock()
    mock_view.btnNavSolicitudes = MagicMock()
    mock_view.btnNavCierre = MagicMock()
    mock_view.btnNavCerrarSesion = MagicMock()
    mock_view.actRevisarPostulaciones = MagicMock()
    mock_view.actGenerarTernas = MagicMock()
    mock_view.actAsignarTutores = MagicMock()
    mock_view.actAutorizacionesPendientes = MagicMock()
    mock_view.actEmitirOficios = MagicMock()
    mock_view.actCierreOficial = MagicMock()
    mock_view.actCerrarSesion = MagicMock()
    mock_view.actSalirSistema = MagicMock()
    mock_view.actAcercaPrograma = MagicMock()
    mock_view.actAcercaDesarrollador = MagicMock()
    mock_view.actRepositorioGithub = MagicMock()
    mock_view.btnValidarPostulacion = MagicMock()
    mock_view.btnRechazarPostulacion = MagicMock()
    mock_view.btnEnviarTerna = MagicMock()
    mock_view.btnAsignarTutor = MagicMock()
    mock_view.btnAprobarAutorizacion = MagicMock()
    mock_view.btnRechazarAutorizacion = MagicMock()
    mock_view.tblPostulacionesPendientes = MagicMock()
    mock_view.tblOfertasConteo = MagicMock()
    mock_view.tblPracticasSinTutor = MagicMock()
    mock_view.tblAutorizacionesPendientes = MagicMock()
    mock_view.tblOficiosPendientes = MagicMock()
    mock_view.tblPracticasActivas = MagicMock()
    mock_view.cmbTutoresDisponibles = MagicMock()
    mock_view.stackedWidgetCentral = MagicMock()
    mock_view.btnEjecutarCierre = MagicMock()


def test_coordinador_controller_enviar_terna_invalida(qapp):
    mock_view = MagicMock()
    configure_mock_coordinador_view(mock_view)

    mock_service = MagicMock()
    mock_service.revisar_postulaciones_pendientes.return_value = []
    mock_service.listar_ofertas_con_conteo_validadas.return_value = []
    mock_service.listar_solicitudes_autorizacion_pendientes.return_value = []
    mock_service.listar_solicitudes_oficio_pendientes.return_value = []
    mock_service.listar_practicas_pendientes_de_tutor.return_value = []

    # Mock selected row conteo: only 2 postulations
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblOfertasConteo.selectedItems.return_value = [selected_item]

    item_id = MagicMock()
    item_id.data.return_value = 999
    mock_view.tblOfertasConteo.item.return_value = item_id

    mock_service.postulacion_repo._datos = [
        MagicMock(id_pos=1, id_o=999, estado_de_postulacion=EstadoPostulacion.VALIDADA),
        MagicMock(id_pos=2, id_o=999, estado_de_postulacion=EstadoPostulacion.VALIDADA),
    ]

    coordinador_perfil = MagicMock()

    with patch("src.controllers.coordinador_controller.uic.loadUi"):
        _controller = CoordinadorController(mock_view, mock_service, coordinador_perfil)

    with patch(
        "src.controllers.coordinador_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes,
    ), patch("src.controllers.coordinador_controller.QMessageBox.warning") as mock_warn:
        _controller.enviar_terna()
        mock_warn.assert_called_once_with(
            mock_view, "Validación", "No existen suficientes postulaciones validadas."
        )
        mock_service.enviar_terna_a_empresa.assert_not_called()


def test_coordinador_controller_enviar_terna_valida(qapp):
    mock_view = MagicMock()
    configure_mock_coordinador_view(mock_view)

    mock_service = MagicMock()
    mock_service.revisar_postulaciones_pendientes.return_value = []
    mock_service.listar_ofertas_con_conteo_validadas.return_value = []
    mock_service.listar_solicitudes_autorizacion_pendientes.return_value = []
    mock_service.listar_solicitudes_oficio_pendientes.return_value = []
    mock_service.listar_practicas_pendientes_de_tutor.return_value = []
    mock_service.enviar_terna_a_empresa.return_value = True

    # Mock selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblOfertasConteo.selectedItems.return_value = [selected_item]

    item_id = MagicMock()
    item_id.data.return_value = 999
    mock_view.tblOfertasConteo.item.return_value = item_id

    mock_service.postulacion_repo._datos = [
        MagicMock(id_pos=10, id_o=999, estado_de_postulacion=EstadoPostulacion.VALIDADA),
        MagicMock(id_pos=11, id_o=999, estado_de_postulacion=EstadoPostulacion.VALIDADA),
        MagicMock(id_pos=12, id_o=999, estado_de_postulacion=EstadoPostulacion.VALIDADA),
    ]

    coordinador_perfil = MagicMock()

    with patch("src.controllers.coordinador_controller.uic.loadUi"):
        _controller = CoordinadorController(mock_view, mock_service, coordinador_perfil)

    with patch(
        "src.controllers.coordinador_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes,
    ), patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info:
        _controller.enviar_terna()
        mock_service.enviar_terna_a_empresa.assert_called_once_with([10, 11, 12])
        mock_info.assert_called_once()


def test_coordinador_controller_evaluar_autorizacion(qapp):
    mock_view = MagicMock()
    configure_mock_coordinador_view(mock_view)

    mock_service = MagicMock()
    mock_service.revisar_postulaciones_pendientes.return_value = []
    mock_service.listar_ofertas_con_conteo_validadas.return_value = []
    mock_service.listar_solicitudes_autorizacion_pendientes.return_value = []
    mock_service.listar_solicitudes_oficio_pendientes.return_value = []
    mock_service.listar_practicas_pendientes_de_tutor.return_value = []
    mock_service.evaluar_solicitud_autorizacion.return_value = True

    # Mock selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblAutorizacionesPendientes.selectedItems.return_value = [selected_item]

    item_id = MagicMock()
    item_id.data.return_value = 77
    mock_view.tblAutorizacionesPendientes.item.return_value = item_id

    coordinador_perfil = MagicMock()
    coordinador_perfil.id_p = 50

    with patch("src.controllers.coordinador_controller.uic.loadUi"):
        _controller = CoordinadorController(mock_view, mock_service, coordinador_perfil)

    with patch(
        "src.controllers.coordinador_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes,
    ), patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info:
        _controller.aprobar_autorizacion()
        mock_service.evaluar_solicitud_autorizacion.assert_called_once_with(
            77, True, 50, "Representante", "Director"
        )
        mock_info.assert_called_once()


def test_coordinador_controller_aprobar_cierre_documentacion_incompleta(qapp):
    mock_view = MagicMock()
    configure_mock_coordinador_view(mock_view)

    mock_service = MagicMock()
    mock_service.revisar_postulaciones_pendientes.return_value = []
    mock_service.listar_ofertas_con_conteo_validadas.return_value = []
    mock_service.listar_solicitudes_autorizacion_pendientes.return_value = []
    mock_service.listar_solicitudes_oficio_pendientes.return_value = []
    mock_service.listar_practicas_pendientes_de_tutor.return_value = []
    mock_service.ejecutar_cierre_oficial_practica.side_effect = DocumentacionIncompletaError(
        "Falta firma de CC y formulario 2"
    )

    # Mock selection
    selected_item = MagicMock()
    selected_item.row.return_value = 0
    mock_view.tblPracticasActivas.selectedItems.return_value = [selected_item]

    item_id = MagicMock()
    item_id.data.return_value = 500
    mock_view.tblPracticasActivas.item.return_value = item_id

    coordinador_perfil = MagicMock()

    with patch("src.controllers.coordinador_controller.uic.loadUi"):
        _controller = CoordinadorController(mock_view, mock_service, coordinador_perfil)

    with patch(
        "src.controllers.coordinador_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes,
    ), patch("src.controllers.coordinador_controller.QMessageBox.critical") as mock_crit:
        _controller.ejecutar_cierre()
        mock_crit.assert_called_with(
            mock_view, "Error de Documentación", "Falta firma de CC y formulario 2"
        )


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

