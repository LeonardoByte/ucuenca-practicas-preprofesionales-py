from datetime import date
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMessageBox

from src.controllers import TutorEmpresarialController
from src.models.estados import EstadoFirmaFormulario
from src.services.exceptions import EvaluacionTempranaError
from src.views import MainWindow_TutorEmpresarial


def setup_mock_service_and_tutor(id_e=10, id_p=5):
    mock_service = MagicMock()

    # Mock tutor profile
    tutor_perfil = MagicMock()
    tutor_perfil.id_e = id_e
    tutor_perfil.id_p = id_p

    # Mock company details
    empresa = MagicMock()
    empresa.nombre_empresa = "Empresa Innovadora"
    empresa.correo_electronico = "tutor@innovadora.com"
    empresa.numeros_contacto = ["0987654321"]
    empresa.direcciones = ["Av. Principal 456"]
    empresa.estado_de_convenio_emp.value = "VIGENTE"
    mock_service.obtener_datos_empresa_tutor.return_value = empresa

    # Mock practices list
    practica1 = MagicMock()
    practica1.id_pr = 1
    practica1.id_pos = 101
    practica1.fecha_inicio = "2026-01-01"
    practica1.fecha_fin = "2026-06-30"
    practica1.estado_de_practica.value = "EN_DESARROLLO"

    mock_service.obtener_practicas_tutor_emp.return_value = [practica1]

    # Mock repositories
    post = MagicMock()
    post.id_p_estudiante = 201
    mock_service.practica_service.postulacion_repo.buscar_por_id.return_value = post

    est = MagicMock()
    est.cedula_dni = "1799887766"
    est.nombre_y_apellido = "Kevin Macias"
    est.correo_electronico = "kevin.macias@ucuenca.edu.ec"
    mock_service.practica_service.estudiante_repo.buscar_por_id.return_value = est
    mock_service.practica_service.practica_repo.buscar_por_id.return_value = practica1

    return mock_service, tutor_perfil


def test_tutor_empresarial_navigation_and_profile_loading(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_tutor()

    view = MainWindow_TutorEmpresarial()
    _controller = TutorEmpresarialController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # Passively populated profile check on page 2 (index 2)
    assert view.txtNombreEmpresa.text() == "Empresa Innovadora"
    assert view.txtCorreoElectronicoEmpresa.text() == "tutor@innovadora.com"
    assert view.txtContactoPrincipalEmpresa.text() == "0987654321"
    assert view.txtDireccionMatrizEmpresa.text() == "Av. Principal 456"
    assert view.txtEstadoConvenio.text() == "VIGENTE"

    # Passively populated student practices check
    assert view.tblPracticas.rowCount() == 1
    assert view.tblPracticas.item(0, 0).text() == "1799887766"  # Cédula
    assert view.tblPracticas.item(0, 1).text() == "Kevin Macias"  # Alumno
    assert view.tblPracticas.item(0, 2).text() == "2026-01-01"
    assert view.tblPracticas.item(0, 3).text() == "2026-06-30"
    assert view.tblPracticas.item(0, 4).text() == "EN_DESARROLLO"

    # StackedWidget index should start at 0
    assert view.stackedWidgetCentral.currentIndex() == 0

    # Navigate to Empresa
    view.btnNavEmpresa.click()
    assert view.stackedWidgetCentral.currentIndex() == 2

    # Navigate to Practicantes
    view.btnNavPracticantes.click()
    assert view.stackedWidgetCentral.currentIndex() == 0


def test_tutor_empresarial_search_filtering(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_tutor()

    # Let's add multiple practices
    practica1 = MagicMock(id_pr=1, id_pos=101, fecha_inicio="2026-01-01", fecha_fin="2026-06-30")
    practica1.estado_de_practica.value = "EN_DESARROLLO"

    practica2 = MagicMock(id_pr=2, id_pos=102, fecha_inicio="2026-01-01", fecha_fin="2026-06-30")
    practica2.estado_de_practica.value = "EN_DESARROLLO"

    mock_service.obtener_practicas_tutor_emp.return_value = [practica1, practica2]

    # We mock repos to return different students based on ID
    post1 = MagicMock(id_p_estudiante=201)
    post2 = MagicMock(id_p_estudiante=202)
    def mock_post_lookup(id_pos):
        return post1 if id_pos == 101 else post2
    mock_service.practica_service.postulacion_repo.buscar_por_id.side_effect = mock_post_lookup

    est1 = MagicMock(
        cedula_dni="1799887766",
        nombre_y_apellido="Kevin Macias",
        correo_electronico="kevin@unl.edu.ec"
    )
    est2 = MagicMock(
        cedula_dni="1799887777",
        nombre_y_apellido="Maria Lopez",
        correo_electronico="maria@unl.edu.ec"
    )
    def mock_est_lookup(id_p):
        return est1 if id_p == 201 else est2
    mock_service.practica_service.estudiante_repo.buscar_por_id.side_effect = mock_est_lookup

    def mock_practica_lookup(id_pr):
        return practica1 if id_pr == 1 else practica2
    mock_service.practica_service.practica_repo.buscar_por_id.side_effect = mock_practica_lookup

    view = MainWindow_TutorEmpresarial()
    _controller = TutorEmpresarialController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    assert view.tblPracticas.rowCount() == 2
    assert not view.tblPracticas.isRowHidden(0)
    assert not view.tblPracticas.isRowHidden(1)

    # Filter by "kevin"
    view.txtBusquedaAlumno.setText("kevin")
    assert not view.tblPracticas.isRowHidden(0)
    assert view.tblPracticas.isRowHidden(1)

    # Clear filter
    view.txtBusquedaAlumno.clear()
    assert not view.tblPracticas.isRowHidden(0)
    assert not view.tblPracticas.isRowHidden(1)


def test_tutor_empresarial_no_selection_warnings(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_tutor()
    view = MainWindow_TutorEmpresarial()
    _controller = TutorEmpresarialController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # Clear table selection
    view.tblPracticas.clearSelection()

    # 1. Click btnVerBitacora without selection -> warning popup
    with patch("src.controllers.tutor_empresarial_controller.QMessageBox.warning") as mock_warning:
        view.btnVerBitacora.click()
        mock_warning.assert_called_once_with(
            view, "Selección requerida", "Debe seleccionar un estudiante de la tabla."
        )

    # 2. Click btnEvaluarFormulario3 without selection -> warning popup
    with patch("src.controllers.tutor_empresarial_controller.QMessageBox.warning") as mock_warning:
        view.btnEvaluarFormulario3.click()
        mock_warning.assert_called_once_with(
            view, "Selección requerida", "Debe seleccionar un estudiante de la tabla."
        )

    # 3. Click btnProponerActividad without selection -> warning popup
    with patch("src.controllers.tutor_empresarial_controller.QMessageBox.warning") as mock_warning:
        view.btnProponerActividad.click()
        mock_warning.assert_called_once_with(
            view, "Selección requerida", "Debe seleccionar un estudiante de la tabla."
        )


def test_tutor_empresarial_propose_activity_workflow(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_tutor()
    view = MainWindow_TutorEmpresarial()
    _controller = TutorEmpresarialController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # Select first row
    view.tblPracticas.selectRow(0)

    # Set up mock activities repo response
    act1 = MagicMock()
    act1.id_pr = 1
    act1.descripcion_de_la_tarea = "Implementar testing"
    act1.estado_de_validacion.value = "EN_ESPERA"

    with patch("src.repositories.ActividadRepository") as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo._datos = [act1]

        # Click btnVerBitacora -> routes to index 1 and loads activities
        view.btnVerBitacora.click()

        assert view.stackedWidgetCentral.currentIndex() == 1
        assert view.tblBitacora.rowCount() == 1
        assert view.tblBitacora.item(0, 0).text() == "Implementar testing"
        assert view.tblBitacora.item(0, 1).text() == "EN_ESPERA"

    # Now try to propose an empty activity
    view.txaDescripcionActividad.setText("")
    with patch("src.controllers.tutor_empresarial_controller.QMessageBox.warning") as mock_warning:
        view.btnProponerActividad.click()
        mock_warning.assert_called_once_with(
            view, "Campo requerido", "Debe ingresar una descripción para la actividad."
        )

    # Propose valid activity
    view.txaDescripcionActividad.setText("Crear base de datos")
    mock_service.proponer_actividad_practica.return_value = MagicMock()

    act2 = MagicMock()
    act2.id_pr = 1
    act2.descripcion_de_la_tarea = "Crear base de datos"
    act2.estado_de_validacion.value = "EN_ESPERA"

    with patch("src.repositories.ActividadRepository") as mock_repo_class, \
         patch("src.controllers.tutor_empresarial_controller.QMessageBox.information") as mock_info:
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo._datos = [act1, act2]

        view.btnProponerActividad.click()

        mock_service.proponer_actividad_practica.assert_called_once_with(1, "Crear base de datos")
        mock_info.assert_called_once_with(
            view, "Actividad Registrada", "La actividad fue guardada correctamente."
        )
        assert view.txaDescripcionActividad.text() == ""
        assert view.tblBitacora.rowCount() == 2
        assert view.tblBitacora.item(1, 0).text() == "Crear base de datos"


def test_tutor_empresarial_evaluar_f3_zero_trust(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_tutor()
    view = MainWindow_TutorEmpresarial()
    _controller = TutorEmpresarialController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # Select first row
    view.tblPracticas.selectRow(0)

    # Case 1: Early evaluation check (more than 7 days left) -> warning popup
    mock_service.registrar_evaluacion_formulario3.side_effect = EvaluacionTempranaError(
        "Faltan más de 7 días para el cierre"
    )

    with patch("src.controllers.tutor_empresarial_controller.QMessageBox.warning") as mock_warning:
        view.btnEvaluarFormulario3.click()

        mock_service.registrar_evaluacion_formulario3.assert_called_with(
            1, EstadoFirmaFormulario.COMPLETADO, date.today().strftime("%Y-%m-%d")
        )
        mock_warning.assert_called_once_with(
            view, "Evaluación Anticipada", "Faltan más de 7 días para el cierre"
        )

    # Case 2: Within range -> success popup
    mock_service.registrar_evaluacion_formulario3.side_effect = None
    mock_service.registrar_evaluacion_formulario3.return_value = True

    with patch("src.controllers.tutor_empresarial_controller.QMessageBox.information") as mock_info:
        view.btnEvaluarFormulario3.click()

        mock_info.assert_called_once_with(
            view, "Evaluación Guardada", "La información fue guardada correctamente."
        )


def test_tutor_empresarial_logout_and_help_dialogs(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_tutor()
    view = MainWindow_TutorEmpresarial()
    controller = TutorEmpresarialController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # 1. Test Logout -> Cancel (No)
    spy = MagicMock()
    controller.cerrar_sesion.connect(spy)

    with patch(
        "src.controllers.tutor_empresarial_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.No
    ):
        view.btnNavCerrarSesion.click()
        spy.assert_not_called()

    # 2. Test Logout -> Confirm (Yes)
    with patch(
        "src.controllers.tutor_empresarial_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes
    ):
        view.btnNavCerrarSesion.click()
        spy.assert_called_once()

    # 3. Test help dialogs
    dialog_instances = []
    def mock_exec_func(self):
        dialog_instances.append(self)
        return 1

    with patch("PyQt6.QtWidgets.QDialog.exec", mock_exec_func):
        # actAcercaPrograma -> index 0
        view.actAcercaPrograma.trigger()
        assert len(dialog_instances) == 1
        assert dialog_instances[-1].stackedWidgetAyuda.currentIndex() == 0

        # actAcercaDesarrollador -> index 1
        view.actAcercaDesarrollador.trigger()
        assert len(dialog_instances) == 2
        assert dialog_instances[-1].stackedWidgetAyuda.currentIndex() == 1

        # actRepositorioGithub -> index 2
        with patch("PyQt6.QtGui.QDesktopServices.openUrl") as mock_open_url:
            view.actRepositorioGithub.trigger()
            assert len(dialog_instances) == 3
            assert dialog_instances[-1].stackedWidgetAyuda.currentIndex() == 2
            mock_open_url.assert_called_once_with(QUrl("https://github.com/LeonardoByte"))
