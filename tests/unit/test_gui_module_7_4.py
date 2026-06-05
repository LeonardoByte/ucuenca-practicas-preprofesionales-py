import json
from datetime import date
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QComboBox, QDialog, QLineEdit, QMessageBox

from src.controllers import EmpresaController
from src.models.estados import EstadoPostulacion
from src.views import MainWindow_Empresa


def setup_mock_service_and_perfil(id_e=10):
    mock_service = MagicMock()
    empresa_perfil = MagicMock()
    empresa_perfil.id_e = id_e

    # Mock tutores list
    tutor1 = MagicMock(
        id_p=101,
        cedula_dni="1799887766",
        nombre_y_apellido="Luis Perez",
        correo_electronico="luis@tech.com",
    )
    tutor2 = MagicMock(
        id_p=102,
        cedula_dni="1122334455",
        nombre_y_apellido="Ana Gomez",
        correo_electronico="ana@tech.com",
    )
    mock_service.obtener_tutores_de_empresa.return_value = [tutor1, tutor2]

    # Mock offers list
    package1 = {"titulo": "Desarrollador Python", "descripcion": "Trabajo con backend"}
    oferta1 = MagicMock(
        id_o=1,
        id_e=id_e,
        descripcion_oferta=json.dumps(package1),
        requisitos="Python, Git",
        fecha_de_publicacion="2026-06-01",
        duracion="3 meses",
        remuneracion=500.0,
    )
    package2 = {"titulo": "Desarrollador Frontend", "descripcion": "Trabajo con React"}
    oferta2 = MagicMock(
        id_o=2,
        id_e=id_e,
        descripcion_oferta=json.dumps(package2),
        requisitos="React, CSS",
        fecha_de_publicacion="2026-06-02",
        duracion="6 meses",
        remuneracion=600.0,
    )
    mock_service.listar_mis_ofertas_publicadas.return_value = [oferta1, oferta2]

    return mock_service, empresa_perfil


def test_empresa_navigation_and_pages(qtbot):
    mock_service, empresa_perfil = setup_mock_service_and_perfil()
    view = MainWindow_Empresa()
    _controller = EmpresaController(view, mock_service, empresa_perfil)
    qtbot.addWidget(view)

    # Starts at Page 1 (index 0)
    assert view.stackedWidgetCentral.currentIndex() == 0

    # Go to Page 2 (Historial)
    view.btnNavHistorial.click()
    assert view.stackedWidgetCentral.currentIndex() == 1

    # Go to Page 4 (Tutores)
    view.btnNavTutores.click()
    assert view.stackedWidgetCentral.currentIndex() == 3

    # Go to Page 1 (Publicar)
    view.btnNavPublicar.click()
    assert view.stackedWidgetCentral.currentIndex() == 0


def test_empresa_publicar_oferta_validation_and_json(qtbot):
    mock_service, empresa_perfil = setup_mock_service_and_perfil()
    view = MainWindow_Empresa()
    _controller = EmpresaController(view, mock_service, empresa_perfil)
    qtbot.addWidget(view)

    # 1. Validation warning (missing title)
    view.txtTituloOferta.setText("")
    view.txaRequisitos.setText("Requisitos dummy")
    with patch("src.controllers.empresa_controller.QMessageBox.warning") as mock_warn:
        view.btnPublicar.click()
        mock_warn.assert_called_once_with(view, "Validación", "Debe ingresar el nombre.")

    # 2. Validation warning (missing requisitos)
    mock_warn.reset_mock()
    view.txtTituloOferta.setText("Titulo dummy")
    view.txaRequisitos.setText("")
    with patch("src.controllers.empresa_controller.QMessageBox.warning") as mock_warn:
        view.btnPublicar.click()
        mock_warn.assert_called_once_with(view, "Validación", "Debe ingresar el nombre.")

    # 3. Successful publishing
    view.txtTituloOferta.setText("Fullstack Dev")
    view.txtDescripcionOferta.setText("Python and React")
    view.txaRequisitos.setText("Git, SQL")
    view.txtDuracionOferta.setText("4 meses")
    view.dspnRemuneracion.setValue(700.0)

    mock_service.registrar_oferta.return_value = MagicMock()

    with patch("src.controllers.empresa_controller.QMessageBox.information") as mock_info:
        view.btnPublicar.click()
        mock_info.assert_called_once()
        expected_json = json.dumps({"titulo": "Fullstack Dev", "descripcion": "Python and React"})
        mock_service.registrar_oferta.assert_called_once_with(
            10, expected_json, "Git, SQL", date.today().strftime("%Y-%m-%d"), "4 meses", 700.0
        )

        # Fields cleared
        assert view.txtTituloOferta.text() == ""
        assert view.txtDescripcionOferta.text() == ""
        assert view.txaRequisitos.text() == ""
        assert view.txtDuracionOferta.text() == ""
        assert view.dspnRemuneracion.value() == 0.0


def test_empresa_historial_table_and_filtering(qtbot):
    mock_service, empresa_perfil = setup_mock_service_and_perfil()
    view = MainWindow_Empresa()
    _controller = EmpresaController(view, mock_service, empresa_perfil)
    qtbot.addWidget(view)

    # Open Page 2 (Historial)
    view.btnNavHistorial.click()

    # Assert 2 rows and deserialized JSON
    assert view.tblOfertasHistorico.rowCount() == 2
    assert view.tblOfertasHistorico.item(0, 0).text() == "Desarrollador Python"
    assert view.tblOfertasHistorico.item(0, 1).text() == "Trabajo con backend"
    assert view.tblOfertasHistorico.item(0, 2).text() == "Python, Git"
    assert view.tblOfertasHistorico.item(0, 3).text() == "2026-06-01"

    assert view.tblOfertasHistorico.item(1, 0).text() == "Desarrollador Frontend"
    assert view.tblOfertasHistorico.item(1, 1).text() == "Trabajo con React"

    # Filter in real time
    view.txtFiltradoOferta.setText("Python")
    assert not view.tblOfertasHistorico.isRowHidden(0)
    assert view.tblOfertasHistorico.isRowHidden(1)

    # Clear filter
    view.txtFiltradoOferta.setText("")
    assert not view.tblOfertasHistorico.isRowHidden(0)
    assert not view.tblOfertasHistorico.isRowHidden(1)


def test_empresa_dar_de_baja(qtbot):
    mock_service, empresa_perfil = setup_mock_service_and_perfil()
    view = MainWindow_Empresa()
    _controller = EmpresaController(view, mock_service, empresa_perfil)
    qtbot.addWidget(view)

    view.btnNavHistorial.click()

    # 1. Click delete without selection -> warning
    view.tblOfertasHistorico.clearSelection()
    with patch("src.controllers.empresa_controller.QMessageBox.warning") as mock_warn:
        view.pushButton.click()  # pushButton is btnDarDeBaja
        mock_warn.assert_called_once()

    # 2. Select first row and delete -> cancel (No)
    view.tblOfertasHistorico.selectRow(0)
    with patch(
        "src.controllers.empresa_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.No,
    ):
        view.pushButton.click()
        mock_service.oferta_service.repo.eliminar.assert_not_called()

    # 3. Select first row and delete -> confirm (Yes)
    mock_service.oferta_service.repo.eliminar.return_value = True
    with patch(
        "src.controllers.empresa_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes,
    ), patch("src.controllers.empresa_controller.QMessageBox.information") as mock_info:
        view.pushButton.click()
        mock_service.oferta_service.repo.eliminar.assert_called_once_with(1)
        mock_info.assert_called_once()


def test_empresa_terna_navigation_and_actions(qtbot):
    mock_service, empresa_perfil = setup_mock_service_and_perfil()
    view = MainWindow_Empresa()
    _controller = EmpresaController(view, mock_service, empresa_perfil)
    qtbot.addWidget(view)

    view.btnNavHistorial.click()

    # 1. View terna without selection -> warning
    view.tblOfertasHistorico.clearSelection()
    with patch("src.controllers.empresa_controller.QMessageBox.warning") as mock_warn:
        view.btnVerTerna.click()
        mock_warn.assert_called_once()

    # 2. Select row, check loading of terna table
    view.tblOfertasHistorico.selectRow(0)

    post1 = MagicMock(id_pos=501, id_o=1, id_terna=99, id_p_estudiante=201)
    post2 = MagicMock(id_pos=502, id_o=1, id_terna=99, id_p_estudiante=202)
    mock_service.postulacion_service.repo._datos = [post1, post2]
    mock_service.visualizar_terna_recibida.return_value = [post1, post2]

    est1 = MagicMock(
        cedula_dni="1722",
        nombre_y_apellido="Estudiante Uno",
        correo_electronico="uno@unl.edu.ec",
    )
    est2 = MagicMock(
        cedula_dni="1733",
        nombre_y_apellido="Estudiante Dos",
        correo_electronico="dos@unl.edu.ec",
    )
    est_map = {201: est1, 202: est2}
    mock_service.practica_service.estudiante_repo.buscar_por_id.side_effect = (
        lambda id_p: est_map.get(id_p)
    )

    view.btnVerTerna.click()
    assert view.stackedWidgetCentral.currentIndex() == 2
    assert view.tblPostulantesTerna.rowCount() == 2
    assert view.tblPostulantesTerna.item(0, 0).text() == "1722"
    assert view.tblPostulantesTerna.item(0, 1).text() == "Estudiante Uno"
    assert view.tblPostulantesTerna.item(0, 2).text() == "uno@unl.edu.ec"

    # 3. Reject postulation
    view.tblPostulantesTerna.selectRow(0)
    mock_service.postulacion_service.cambiar_estado.return_value = True

    # Need to mock property for reloading
    view.tblPostulantesTerna.setProperty("current_id_o", 1)

    with patch("src.controllers.empresa_controller.QMessageBox.information") as mock_info:
        view.btnRechazarPostulacion.click()
        mock_service.postulacion_service.cambiar_estado.assert_called_once_with(
            501, EstadoPostulacion.RECHAZADA
        )
        mock_info.assert_called_once()

    # 4. Accept postulation and formalise (mock Dialog inputs)
    view.tblPostulantesTerna.selectRow(0)
    mock_service.seleccionar_candidato_ganador.return_value = True

    def mock_dialog_exec(self):
        combos = self.findChildren(QComboBox)
        line_edits = self.findChildren(QLineEdit)
        if combos:
            combos[0].setCurrentIndex(0)
        if len(line_edits) >= 2:
            line_edits[0].setText("2026-06-05")
            line_edits[1].setText("2026-12-05")
        return QDialog.DialogCode.Accepted

    with patch("src.controllers.empresa_controller.QDialog.exec", mock_dialog_exec), \
         patch("src.controllers.empresa_controller.QMessageBox.information") as mock_info:
        view.btnAceptarPostulacion.click()
        # Luis Perez's tutor ID is 101
        mock_service.seleccionar_candidato_ganador.assert_called_once_with(
            501, 101, "2026-06-05", "2026-12-05"
        )
        mock_info.assert_called_once()
        # Returns to history
        assert view.stackedWidgetCentral.currentIndex() == 1


def test_empresa_tutores_table_and_filtering(qtbot):
    mock_service, empresa_perfil = setup_mock_service_and_perfil()
    view = MainWindow_Empresa()
    _controller = EmpresaController(view, mock_service, empresa_perfil)
    qtbot.addWidget(view)

    # Go to Page 4 (Tutores)
    view.btnNavTutores.click()

    # Assert 2 rows loaded
    assert view.tableWidget.rowCount() == 2
    assert view.tableWidget.item(0, 0).text() == "1799887766"
    assert view.tableWidget.item(0, 1).text() == "Luis Perez"
    assert view.tableWidget.item(0, 2).text() == "luis@tech.com"

    # Filter Tutores by email
    view.txtBusquedaTutor.setText("ana")
    assert view.tableWidget.isRowHidden(0)
    assert not view.tableWidget.isRowHidden(1)


def test_empresa_logout_and_help_dialogs(qtbot):
    mock_service, empresa_perfil = setup_mock_service_and_perfil()
    view = MainWindow_Empresa()
    controller = EmpresaController(view, mock_service, empresa_perfil)
    qtbot.addWidget(view)

    spy = MagicMock()
    controller.cerrar_sesion.connect(spy)

    # 1. Logout Cancel
    with patch(
        "src.controllers.empresa_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.No,
    ):
        view.btnNavCerrarSesion.click()
        spy.assert_not_called()

    # 2. Logout Confirm
    with patch(
        "src.controllers.empresa_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes,
    ):
        view.btnNavCerrarSesion.click()
        spy.assert_called_once()

    # 3. Help dialogs
    dialog_instances = []
    def mock_exec_func(self):
        dialog_instances.append(self)
        return 1

    with patch("PyQt6.QtWidgets.QDialog.exec", mock_exec_func):
        view.actAcercaPrograma.trigger()
        assert len(dialog_instances) == 1
        assert dialog_instances[-1].stackedWidgetAyuda.currentIndex() == 0

        view.actAcercaDesarrollador.trigger()
        assert len(dialog_instances) == 2
        assert dialog_instances[-1].stackedWidgetAyuda.currentIndex() == 1

        with patch("PyQt6.QtGui.QDesktopServices.openUrl") as mock_open_url:
            view.actRepositorioGithub.trigger()
            assert len(dialog_instances) == 3
            assert dialog_instances[-1].stackedWidgetAyuda.currentIndex() == 2
            mock_open_url.assert_called_once_with(QUrl("https://github.com/LeonardoByte"))
