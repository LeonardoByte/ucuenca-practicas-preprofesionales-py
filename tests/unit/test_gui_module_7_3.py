from datetime import date
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QComboBox, QDialog, QMessageBox

from src.controllers import TutorAcademicoController, TutorEmpresarialController
from src.models.estados import EstadoFirmaFormulario, EstadoValidacionActividad
from src.views import MainWindow_TutorAcademico, MainWindow_TutorEmpresarial

# ==========================================
# 1. Helpers de Mocking
# ==========================================

def setup_mock_service_and_acad_tutor(id_p=12):
    mock_service = MagicMock()

    tutor_perfil = MagicMock()
    tutor_perfil.id_p = id_p

    practica1 = MagicMock()
    practica1.id_pr = 1
    practica1.id_pos = 101
    practica1.fecha_inicio = "2026-01-01"
    practica1.fecha_fin = "2026-06-03"  # within 7 days of 2026-06-01
    practica1.estado_de_practica.value = "EN_DESARROLLO"

    mock_service.obtener_practicas_tutor_acad.return_value = [practica1]

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


def setup_mock_service_and_emp_tutor(id_e=10, id_p=5):
    mock_service = MagicMock()

    tutor_perfil = MagicMock()
    tutor_perfil.id_e = id_e
    tutor_perfil.id_p = id_p

    empresa = MagicMock()
    empresa.nombre_empresa = "Empresa Innovadora"
    empresa.correo_electronico = "tutor@innovadora.com"
    empresa.numeros_contacto = ["0987654321"]
    empresa.direcciones = ["Av. Principal 456"]
    empresa.estado_de_convenio_emp.value = "VIGENTE"
    mock_service.obtener_datos_empresa_tutor.return_value = empresa

    practica1 = MagicMock()
    practica1.id_pr = 1
    practica1.id_pos = 101
    practica1.fecha_inicio = "2026-01-01"
    practica1.fecha_fin = "2026-06-30"
    practica1.estado_de_practica.value = "EN_DESARROLLO"

    mock_service.obtener_practicas_tutor_emp.return_value = [practica1]

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


# ==========================================
# 2. Pruebas de Tutor Empresarial (Actualización)
# ==========================================

def test_tutor_empresarial_updated_grid_and_search(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_emp_tutor()

    # 2 practices for filtering testing
    practica1 = MagicMock(id_pr=1, id_pos=101, fecha_inicio="2026-01-01", fecha_fin="2026-06-30")
    practica1.estado_de_practica.value = "EN_DESARROLLO"
    practica2 = MagicMock(id_pr=2, id_pos=102, fecha_inicio="2026-01-01", fecha_fin="2026-06-30")
    practica2.estado_de_practica.value = "EN_DESARROLLO"
    mock_service.obtener_practicas_tutor_emp.return_value = [practica1, practica2]

    post1 = MagicMock(id_p_estudiante=201)
    post2 = MagicMock(id_p_estudiante=202)
    post_map = {101: post1, 102: post2}
    mock_service.practica_service.postulacion_repo.buscar_por_id.side_effect = (
        lambda id_pos: post_map.get(id_pos)
    )

    est1 = MagicMock(
        cedula_dni="1799887766",
        nombre_y_apellido="Kevin Macias",
        correo_electronico="kevin@unl.edu.ec"
    )
    est2 = MagicMock(
        cedula_dni="1122334455",
        nombre_y_apellido="Maria Lopez",
        correo_electronico="maria@unl.edu.ec"
    )
    est_map = {201: est1, 202: est2}
    mock_service.practica_service.estudiante_repo.buscar_por_id.side_effect = (
        lambda id_p: est_map.get(id_p)
    )
    practica_map = {1: practica1, 2: practica2}
    mock_service.practica_service.practica_repo.buscar_por_id.side_effect = (
        lambda id_pr: practica_map.get(id_pr)
    )

    view = MainWindow_TutorEmpresarial()
    _controller = TutorEmpresarialController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # Column 1 should now be Correo electrónico
    assert view.tblPracticas.columnCount() == 6
    assert view.tblPracticas.item(0, 0).text() == "1799887766"
    assert view.tblPracticas.item(0, 1).text() == "kevin@unl.edu.ec"
    assert view.tblPracticas.item(0, 2).text() == "Kevin Macias"

    # Filter by DNI
    view.txtBusquedaAlumno.setText("1122")
    assert view.tblPracticas.isRowHidden(0)
    assert not view.tblPracticas.isRowHidden(1)

    # Filter by Email
    view.txtBusquedaAlumno.setText("kevin")
    assert not view.tblPracticas.isRowHidden(0)
    assert view.tblPracticas.isRowHidden(1)


# ==========================================
# 3. Pruebas de Tutor Académico
# ==========================================

def test_tutor_academico_navigation_and_profile_loading(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_acad_tutor()

    view = MainWindow_TutorAcademico()
    _controller = TutorAcademicoController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # Passively populated student practices check
    assert view.tblEstudiantes.rowCount() == 1
    assert view.tblEstudiantes.item(0, 0).text() == "1799887766"  # Cédula
    assert view.tblEstudiantes.item(0, 1).text() == "kevin.macias@ucuenca.edu.ec"  # Correo
    assert view.tblEstudiantes.item(0, 2).text() == "Kevin Macias"  # Alumno
    assert view.tblEstudiantes.item(0, 3).text() == "2026-01-01"
    assert view.tblEstudiantes.item(0, 4).text() == "2026-06-03"
    assert view.tblEstudiantes.item(0, 5).text() == "EN_DESARROLLO"

    # Navigation triggers
    assert view.stackedWidgetCentral.currentIndex() == 0

    # Sidebar Auditar Bitacora without selection -> warning
    view.tblEstudiantes.clearSelection()
    with patch("src.controllers.tutor_academico_controller.QMessageBox.warning") as mock_warning:
        view.pushButton_2.click()  # btnNavBitacora
        mock_warning.assert_called_once()
        assert view.stackedWidgetCentral.currentIndex() == 0

    # With selection
    view.tblEstudiantes.selectRow(0)
    view.pushButton_2.click()
    assert view.stackedWidgetCentral.currentIndex() == 1

    # Go back to students
    view.pushButton.click()  # btnNavEstudiantes
    assert view.stackedWidgetCentral.currentIndex() == 0


def test_tutor_academico_search_filtering(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_acad_tutor()

    practica1 = MagicMock(id_pr=1, id_pos=101, fecha_inicio="2026-01-01", fecha_fin="2026-06-03")
    practica1.estado_de_practica.value = "EN_DESARROLLO"
    practica2 = MagicMock(id_pr=2, id_pos=102, fecha_inicio="2026-01-01", fecha_fin="2026-06-03")
    practica2.estado_de_practica.value = "EN_DESARROLLO"
    mock_service.obtener_practicas_tutor_acad.return_value = [practica1, practica2]

    post1 = MagicMock(id_p_estudiante=201)
    post2 = MagicMock(id_p_estudiante=202)
    post_map = {101: post1, 102: post2}
    mock_service.practica_service.postulacion_repo.buscar_por_id.side_effect = (
        lambda id_pos: post_map.get(id_pos)
    )

    est1 = MagicMock(
        cedula_dni="1799887766",
        nombre_y_apellido="Kevin Macias",
        correo_electronico="kevin@unl.edu.ec"
    )
    est2 = MagicMock(
        cedula_dni="1122334455",
        nombre_y_apellido="Maria Lopez",
        correo_electronico="maria@unl.edu.ec"
    )
    est_map = {201: est1, 202: est2}
    mock_service.practica_service.estudiante_repo.buscar_por_id.side_effect = (
        lambda id_p: est_map.get(id_p)
    )
    practica_map = {1: practica1, 2: practica2}
    mock_service.practica_service.practica_repo.buscar_por_id.side_effect = (
        lambda id_pr: practica_map.get(id_pr)
    )

    view = MainWindow_TutorAcademico()
    _controller = TutorAcademicoController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # Filter by DNI
    view.txtBusquedaEstudiante.setText("1122")
    assert view.tblEstudiantes.isRowHidden(0)
    assert not view.tblEstudiantes.isRowHidden(1)

    # Filter by Email
    view.txtBusquedaEstudiante.setText("kevin")
    assert not view.tblEstudiantes.isRowHidden(0)
    assert view.tblEstudiantes.isRowHidden(1)


def test_tutor_academico_bitacora_validation_workflow(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_acad_tutor()
    view = MainWindow_TutorAcademico()
    _controller = TutorAcademicoController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    view.tblEstudiantes.selectRow(0)

    act1 = MagicMock()
    act1.id_act = 501
    act1.descripcion_de_la_tarea = "Configurar base de datos"
    act1.estado_de_validacion.value = "PROPUESTA"
    mock_service.listar_actividades_de_practica.return_value = [act1]

    view.btnAuditarBitacora.click()
    assert view.stackedWidgetCentral.currentIndex() == 1
    assert view.tblBitacoraAuditoria.rowCount() == 1
    assert view.tblBitacoraAuditoria.item(0, 0).text() == "Configurar base de datos"

    # Validate activity
    view.tblBitacoraAuditoria.selectRow(0)
    mock_service.evaluar_actividad_alumno.return_value = True
    with patch("src.controllers.tutor_academico_controller.QMessageBox.information") as mock_info:
        view.btnValidarActividad.click()
        mock_service.evaluar_actividad_alumno.assert_called_once_with(
            501, 1, EstadoValidacionActividad.VALIDADA
        )
        mock_info.assert_called_once()

    # Reject activity
    mock_service.evaluar_actividad_alumno.reset_mock()
    view.tblBitacoraAuditoria.selectRow(0)
    with patch("src.controllers.tutor_academico_controller.QMessageBox.information") as mock_info:
        view.btnRechazarActividad.click()
        mock_service.evaluar_actividad_alumno.assert_called_once_with(
            501, 1, EstadoValidacionActividad.RECHAZADA
        )
        mock_info.assert_called_once()


def test_tutor_academico_formulario2_zero_trust(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_acad_tutor()
    view = MainWindow_TutorAcademico()
    _controller = TutorAcademicoController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # Select student
    view.tblEstudiantes.selectRow(0)

    # Case 1: Early evaluation check (more than 7 days left) -> warning popup & disabled
    practica_early = MagicMock()
    # 2026-06-15 is > 7 days from today (2026-06-01)
    practica_early.fecha_fin = "2026-06-15"
    mock_service.practica_service.practica_repo.buscar_por_id.return_value = practica_early

    with patch("src.controllers.tutor_academico_controller.QMessageBox.warning") as mock_warning:
        view.btnEvaluarFormulario2.click()
        mock_warning.assert_called_once()
        assert not view.btnEvaluarFormulario2.isEnabled()

    # Re-enable for opportune check
    view.btnEvaluarFormulario2.setEnabled(True)
    practica_opportune = MagicMock()
    # 2026-06-03 is within 7 days from 2026-06-01
    practica_opportune.fecha_fin = "2026-06-03"
    mock_service.practica_service.practica_repo.buscar_por_id.return_value = practica_opportune

    mock_service.registrar_evaluacion_formulario2.return_value = True

    # Mocking dynamic QDialog inputs and button connections
    def mock_dialog_exec(self):
        # Programmatically trigger combo currentData to be COMPLETADO
        self.findChild(QComboBox).setCurrentIndex(1)  # Index 1 = COMPLETADO
        return QDialog.DialogCode.Accepted

    with patch("src.controllers.tutor_academico_controller.QDialog.exec", mock_dialog_exec), \
         patch("src.controllers.tutor_academico_controller.QMessageBox.information") as mock_info:
        view.btnEvaluarFormulario2.click()
        mock_service.registrar_evaluacion_formulario2.assert_called_once_with(
            1, EstadoFirmaFormulario.COMPLETADO, date.today().strftime("%Y-%m-%d")
        )
        mock_info.assert_called_once_with(
            view, "Evaluación Guardada", "La información fue guardada correctamente."
        )


def test_tutor_academico_logout_and_help_dialogs(qtbot):
    mock_service, tutor_perfil = setup_mock_service_and_acad_tutor()
    view = MainWindow_TutorAcademico()
    controller = TutorAcademicoController(view, mock_service, tutor_perfil)
    qtbot.addWidget(view)

    # 1. Test Logout -> Cancel (No)
    spy = MagicMock()
    controller.cerrar_sesion.connect(spy)

    with patch(
        "src.controllers.tutor_academico_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.No
    ):
        view.pushButton_3.click()  # btnNavCerrarSesion
        spy.assert_not_called()

    # 2. Test Logout -> Confirm (Yes)
    with patch(
        "src.controllers.tutor_academico_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes
    ):
        view.pushButton_3.click()
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
