import json
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMessageBox

from src.controllers import EstudianteController
from src.services.exceptions import (
    EstudianteConPracticaActivaError,
)
from src.views import MainWindow_Estudiante


def setup_estudiante_test():
    mock_service = MagicMock()
    mock_estudiante_perfil = MagicMock()
    mock_estudiante_perfil.id_p = 33
    mock_estudiante_perfil.nombre_y_apellido = "Estudiante de Prueba"
    mock_estudiante_perfil.correo_electronico = "estudiante@prueba.com"

    # Mock repos
    mock_empresa_repo = MagicMock()
    mock_oferta_repo = MagicMock()
    mock_postulacion_repo = MagicMock()
    mock_actividad_repo = MagicMock()

    # Stub searches
    emp1 = MagicMock(id_e=10, nombre_empresa="Empresa Uno")
    emp2 = MagicMock(id_e=20, nombre_empresa="Empresa Dos")
    emp_map = {10: emp1, 20: emp2}
    mock_empresa_repo.buscar_por_id.side_effect = lambda x: emp_map.get(x)

    oferta1 = MagicMock(
        id_o=101,
        id_e=10,
        descripcion_oferta=json.dumps({"titulo": "Developer Python"}),
        duracion="3 meses",
        remuneracion=500.0,
        requisitos="Python",
    )
    oferta2 = MagicMock(
        id_o=102,
        id_e=20,
        descripcion_oferta=json.dumps({"titulo": "Frontend React"}),
        duracion="6 meses",
        remuneracion=600.0,
        requisitos="React",
    )
    oferta_map = {101: oferta1, 102: oferta2}
    mock_oferta_repo.buscar_por_id.side_effect = lambda x: oferta_map.get(x)

    # Stub service methods
    # Page 1: Ofertas
    mock_service.obtener_catalogo_ofertas.return_value = [oferta1, oferta2]

    # Page 2: Mis Postulaciones
    post1 = MagicMock(id_pos=1, id_o=101, id_e=10, estado_de_postulacion="Pendiente")
    mock_service.obtener_mis_postulaciones.return_value = [post1]

    # Page 4: Bitacora & Practica Activa
    pr_act = MagicMock(id_pr=55, id_pos=1, estado_de_practica="Iniciada")
    mock_service.obtener_practica_activa_estudiante.return_value = pr_act

    act1 = MagicMock(
        id_act=1,
        id_pr=55,
        descripcion_de_la_tarea="Codificar interfaces de usuario",
        estado_de_validacion="Propuesta",
    )
    mock_actividad_repo.listar_por_practica.return_value = [act1]

    return {
        "service": mock_service,
        "estudiante_perfil": mock_estudiante_perfil,
        "empresa_repo": mock_empresa_repo,
        "oferta_repo": mock_oferta_repo,
        "postulacion_repo": mock_postulacion_repo,
        "actividad_repo": mock_actividad_repo,
        "practica_activa": pr_act,
    }


def test_estudiante_navigation_sidebar_and_menubar(qtbot):
    mocks = setup_estudiante_test()

    with (
        patch(
            "src.controllers.estudiante_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.OfertaRepository",
            return_value=mocks["oferta_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.PostulacionRepository",
            return_value=mocks["postulacion_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.ActividadRepository",
            return_value=mocks["actividad_repo"],
        ),
    ):
        view = MainWindow_Estudiante()
        _controller = EstudianteController(view, mocks["service"], mocks["estudiante_perfil"])
        qtbot.addWidget(view)

        # Starts at page index 0 (Ofertas)
        assert view.stackedWidgetCentral.currentIndex() == 0

        # Sidebar navigation
        view.btnNavPostulaciones.click()
        assert view.stackedWidgetCentral.currentIndex() == 1

        view.btnNavSolicitar.click()
        assert view.stackedWidgetCentral.currentIndex() == 2

        view.btnNavBitacora.click()
        assert view.stackedWidgetCentral.currentIndex() == 4

        view.btnNavOfertas.click()
        assert view.stackedWidgetCentral.currentIndex() == 0

        # Menubar trigger actions
        view.actMisPostulaciones.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 1

        view.actSolicitarAutorizacion.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 2

        view.actVerActividades.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 4

        view.actRegistrarActividad.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 4

        view.actVerOfertas.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 0


def test_estudiante_catalogo_loading_and_filtering(qtbot):
    mocks = setup_estudiante_test()

    with (
        patch(
            "src.controllers.estudiante_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.OfertaRepository",
            return_value=mocks["oferta_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.PostulacionRepository",
            return_value=mocks["postulacion_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.ActividadRepository",
            return_value=mocks["actividad_repo"],
        ),
    ):
        view = MainWindow_Estudiante()
        _controller = EstudianteController(view, mocks["service"], mocks["estudiante_perfil"])
        qtbot.addWidget(view)

        # Assert 2 rows loaded
        assert view.tblOfertasDisponibles.rowCount() == 2
        assert view.tblOfertasDisponibles.item(0, 0).text() == "Developer Python"
        assert view.tblOfertasDisponibles.item(0, 1).text() == "Empresa Uno"
        assert view.tblOfertasDisponibles.item(0, 2).text() == "3 meses"
        assert view.tblOfertasDisponibles.item(0, 3).text() == "$500.00"
        assert view.tblOfertasDisponibles.item(0, 4).text() == "Python"

        # Search filter
        view.txtFiltradoOfertas.setText("Python")
        assert not view.tblOfertasDisponibles.isRowHidden(0)
        assert view.tblOfertasDisponibles.isRowHidden(1)

        view.txtFiltradoOfertas.clear()
        assert not view.tblOfertasDisponibles.isRowHidden(0)
        assert not view.tblOfertasDisponibles.isRowHidden(1)


def test_estudiante_postulacion_workflow(qtbot):
    mocks = setup_estudiante_test()

    with (
        patch(
            "src.controllers.estudiante_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.OfertaRepository",
            return_value=mocks["oferta_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.PostulacionRepository",
            return_value=mocks["postulacion_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.ActividadRepository",
            return_value=mocks["actividad_repo"],
        ),
    ):
        view = MainWindow_Estudiante()
        _controller = EstudianteController(view, mocks["service"], mocks["estudiante_perfil"])
        qtbot.addWidget(view)

        # 1. Postulate without selection -> warning
        view.tblOfertasDisponibles.clearSelection()
        with patch("src.controllers.estudiante_controller.QMessageBox.warning") as mock_warn:
            view.btnPostularOferta.click()
            mock_warn.assert_called_once_with(
                view, "Selección requerida", "Debe seleccionar una oferta."
            )

        # 2. Select first row, cancel confirmation (No)
        view.tblOfertasDisponibles.selectRow(0)
        with patch(
            "src.controllers.estudiante_controller.QMessageBox.question",
            return_value=QMessageBox.StandardButton.No,
        ):
            view.btnPostularOferta.click()
            mocks["service"].solicitar_postulacion.assert_not_called()

        # 3. Select first row, accept confirmation (Yes) -> success info
        mocks["service"].solicitar_postulacion.return_value = MagicMock()
        with (
            patch(
                "src.controllers.estudiante_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.estudiante_controller.QMessageBox.information") as mock_info,
        ):
            view.btnPostularOferta.click()
            mocks["service"].solicitar_postulacion.assert_called_once()
            mock_info.assert_called_once_with(view, "Éxito", "Postulación enviada correctamente.")

        # 4. Error flow (RequisitosNoCumplidosError / EstudianteConPracticaActivaError)
        mocks["service"].solicitar_postulacion.reset_mock()
        mocks["service"].solicitar_postulacion.side_effect = EstudianteConPracticaActivaError(
            "Práctica activa."
        )
        view.tblOfertasDisponibles.selectRow(0)
        with (
            patch(
                "src.controllers.estudiante_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.estudiante_controller.QMessageBox.critical") as mock_crit,
        ):
            view.btnPostularOferta.click()
            mock_crit.assert_called_once()


def test_estudiante_postulaciones_historial(qtbot):
    mocks = setup_estudiante_test()

    with (
        patch(
            "src.controllers.estudiante_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.OfertaRepository",
            return_value=mocks["oferta_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.PostulacionRepository",
            return_value=mocks["postulacion_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.ActividadRepository",
            return_value=mocks["actividad_repo"],
        ),
    ):
        view = MainWindow_Estudiante()
        _controller = EstudianteController(view, mocks["service"], mocks["estudiante_perfil"])
        qtbot.addWidget(view)

        view.btnNavPostulaciones.click()

        # Assert 1 row loaded in Mis Postulaciones
        assert view.tblMisPostulaciones.rowCount() == 1
        assert view.tblMisPostulaciones.item(0, 0).text() == "101"
        assert view.tblMisPostulaciones.item(0, 1).text() == "Developer Python"
        assert view.tblMisPostulaciones.item(0, 2).text() == "Empresa Uno"
        assert view.tblMisPostulaciones.item(0, 3).text() == "Pendiente"


def test_estudiante_solicitud_autorizacion_workflow(qtbot):
    mocks = setup_estudiante_test()

    with (
        patch(
            "src.controllers.estudiante_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.OfertaRepository",
            return_value=mocks["oferta_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.PostulacionRepository",
            return_value=mocks["postulacion_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.ActividadRepository",
            return_value=mocks["actividad_repo"],
        ),
    ):
        view = MainWindow_Estudiante()
        _controller = EstudianteController(view, mocks["service"], mocks["estudiante_perfil"])
        qtbot.addWidget(view)

        view.btnNavSolicitar.click()

        # 1. Empty fields validation warning -> "Debe ingresar el nombre."
        view.txtNombreEmpresa.setText("")
        view.txtDetallesEmpresa.setText("Detalles")
        with patch("src.controllers.estudiante_controller.QMessageBox.warning") as mock_warn:
            view.btnEnviarSolicitud.click()
            mock_warn.assert_called_once_with(view, "Campos vacíos", "Debe ingresar el nombre.")

        # 2. Complete fields, confirm (No)
        mock_warn.reset_mock()
        view.txtNombreEmpresa.setText("New Company")
        view.txtDetallesEmpresa.setText("Some Details")
        with patch(
            "src.controllers.estudiante_controller.QMessageBox.question",
            return_value=QMessageBox.StandardButton.No,
        ):
            view.btnEnviarSolicitud.click()
            mocks["service"].registrar_solicitud_autorizacion.assert_not_called()

        # 3. Complete fields, confirm (Yes) -> info message success
        mocks["service"].registrar_solicitud_autorizacion.return_value = MagicMock()
        with (
            patch(
                "src.controllers.estudiante_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.estudiante_controller.QMessageBox.information") as mock_info,
        ):
            view.btnEnviarSolicitud.click()
            mocks["service"].registrar_solicitud_autorizacion.assert_called_once()
            mock_info.assert_called_once_with(
                view, "Éxito", "La información fue guardada correctamente."
            )

            # Fields cleared
            assert view.txtNombreEmpresa.text() == ""
            assert view.txtDetallesEmpresa.text() == ""


def test_estudiante_bitacora_blocking_and_recording(qtbot):
    mocks = setup_estudiante_test()

    # Case A: Has active practice -> unlocked
    with (
        patch(
            "src.controllers.estudiante_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.OfertaRepository",
            return_value=mocks["oferta_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.PostulacionRepository",
            return_value=mocks["postulacion_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.ActividadRepository",
            return_value=mocks["actividad_repo"],
        ),
    ):
        view = MainWindow_Estudiante()
        _controller = EstudianteController(view, mocks["service"], mocks["estudiante_perfil"])
        qtbot.addWidget(view)

        view.btnNavBitacora.click()

        # Table loads activity and inputs are enabled
        assert view.tblMisActividades.rowCount() == 1
        assert view.tblMisActividades.item(0, 0).text() == "Codificar interfaces de usuario"
        assert view.tblMisActividades.item(0, 1).text() == "Propuesta"
        assert view.txaDescripcionActividad.isEnabled()
        assert view.btnProponerActividad.isEnabled()

        # 1. Submit empty activity description -> warning "Debe ingresar el nombre."
        view.txaDescripcionActividad.setText("")
        with patch("src.controllers.estudiante_controller.QMessageBox.warning") as mock_warn:
            view.btnProponerActividad.click()
            mock_warn.assert_called_once_with(view, "Campos vacíos", "Debe ingresar el nombre.")

        # 2. Submit activity description, confirm (Yes) -> success info
        view.txaDescripcionActividad.setText("Escribir pruebas unitarias")
        mocks["service"].registrar_actividad_bitacora.return_value = MagicMock()
        with (
            patch(
                "src.controllers.estudiante_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.estudiante_controller.QMessageBox.information") as mock_info,
        ):
            view.btnProponerActividad.click()
            mocks["service"].registrar_actividad_bitacora.assert_called_once()
            mock_info.assert_called_once_with(
                view, "Éxito", "La información fue guardada correctamente."
            )
            assert view.txaDescripcionActividad.text() == ""


def test_estudiante_bitacora_blocked_if_no_practice(qtbot):
    mocks = setup_estudiante_test()
    # No active practice
    mocks["service"].obtener_practica_activa_estudiante.return_value = None

    with (
        patch(
            "src.controllers.estudiante_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.OfertaRepository",
            return_value=mocks["oferta_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.PostulacionRepository",
            return_value=mocks["postulacion_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.ActividadRepository",
            return_value=mocks["actividad_repo"],
        ),
    ):
        view = MainWindow_Estudiante()
        _controller = EstudianteController(view, mocks["service"], mocks["estudiante_perfil"])
        qtbot.addWidget(view)

        view.btnNavBitacora.click()

        # Table is empty, inputs blocked
        assert view.tblMisActividades.rowCount() == 0
        assert not view.txaDescripcionActividad.isEnabled()
        assert not view.btnProponerActividad.isEnabled()


def test_estudiante_logout_and_help_dialogs(qtbot):
    mocks = setup_estudiante_test()

    with (
        patch(
            "src.controllers.estudiante_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.OfertaRepository",
            return_value=mocks["oferta_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.PostulacionRepository",
            return_value=mocks["postulacion_repo"],
        ),
        patch(
            "src.controllers.estudiante_controller.ActividadRepository",
            return_value=mocks["actividad_repo"],
        ),
    ):
        view = MainWindow_Estudiante()
        controller = EstudianteController(view, mocks["service"], mocks["estudiante_perfil"])
        qtbot.addWidget(view)

        spy = MagicMock()
        controller.cerrar_sesion.connect(spy)

        # Logout Cancel
        with patch(
            "src.controllers.estudiante_controller.QMessageBox.question",
            return_value=QMessageBox.StandardButton.No,
        ):
            view.btnNavCerrarSesion.click()
            spy.assert_not_called()

        # Logout Confirm
        with patch(
            "src.controllers.estudiante_controller.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            view.btnNavCerrarSesion.click()
            spy.assert_called_once()

        # Help dialogs
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


def test_estudiante_practica_activa_y_pdf_workflow(qtbot):
    mocks = setup_estudiante_test()
    pr_act = mocks["practica_activa"]
    pr_act.id_p_tutor_acad = 11
    pr_act.id_p_tutor_emp = 22
    pr_act.fecha_inicio = "2026-06-01"
    pr_act.fecha_fin = "2026-09-01"
    pr_act.estado_de_practica = MagicMock(value="EN_DESARROLLO")

    tutor_acad = MagicMock(nombre_y_apellido="Ing. Marcos Paz")
    tutor_emp = MagicMock(nombre_y_apellido="Dr. Carlos Slim")

    with (
        patch("src.controllers.estudiante_controller.EmpresaRepository", return_value=mocks["empresa_repo"]),
        patch("src.controllers.estudiante_controller.OfertaRepository", return_value=mocks["oferta_repo"]),
        patch("src.controllers.estudiante_controller.PostulacionRepository", return_value=mocks["postulacion_repo"]),
        patch("src.controllers.estudiante_controller.ActividadRepository", return_value=mocks["actividad_repo"]),
        patch("src.repositories.TutorAcademicoRepository") as mock_tutor_acad_repo_class,
        patch("src.repositories.TutorEmpresarialRepository") as mock_tutor_emp_repo_class,
    ):
        mock_t_acad_repo = MagicMock()
        mock_tutor_acad_repo_class.return_value = mock_t_acad_repo
        mock_t_acad_repo.buscar_por_id.return_value = tutor_acad

        mock_t_emp_repo = MagicMock()
        mock_tutor_emp_repo_class.return_value = mock_t_emp_repo
        mock_t_emp_repo.buscar_por_id.return_value = tutor_emp

        view = MainWindow_Estudiante()
        controller = EstudianteController(view, mocks["service"], mocks["estudiante_perfil"])
        qtbot.addWidget(view)

        # Trigger passive active practice info load
        controller.ir_a_practica()

        # Check index
        assert view.stackedWidgetCentral.currentIndex() == 3

        # Check loaded values
        assert view.lbPracticaTutorAcad.text() == "Ing. Marcos Paz"
        assert view.lbPracticaTutorEmpr.text() == "Dr. Carlos Slim"
        assert view.lbPracticaFechaIni.text() == "2026-06-01"
        assert view.lbPracticaFechaFin.text() == "2026-09-01"

        # Check F1 Download
        with patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=("/tmp/form_1.pdf", "PDF Files (*.pdf)")), \
             patch("shutil.copy") as mock_copy, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("src.controllers.estudiante_controller.QMessageBox.information") as mock_info, \
             patch("src.controllers.estudiante_controller.QMessageBox.warning") as mock_warn, \
             patch("src.controllers.estudiante_controller.QMessageBox.critical") as mock_crit:
            view.btnDescargarForm1.click()
            mock_copy.assert_called_once()
            mock_info.assert_called_once()

        # Check F1 Upload
        with patch("PyQt6.QtWidgets.QFileDialog.getOpenFileName", return_value=("/tmp/signed_form_1.pdf", "PDF Files (*.pdf)")), \
             patch("shutil.copy") as mock_copy, \
             patch("src.repositories.FormularioRepository") as mock_form_repo_class, \
             patch("src.controllers.estudiante_controller.QMessageBox.information") as mock_info, \
             patch("src.controllers.estudiante_controller.QMessageBox.warning") as mock_warn, \
             patch("src.controllers.estudiante_controller.QMessageBox.critical") as mock_crit:
            mock_form_repo = MagicMock()
            mock_form_repo_class.return_value = mock_form_repo
            mock_form_repo.listar_formularios_por_practica.return_value = []
            mock_form_repo._datos = []

            view.btnSubirForm1.click()
            mock_form_repo.guardar.assert_called_once()
            mock_info.assert_called_once()


def test_estudiante_catalogo_oculta_ofertas_inactivas_y_qss(qtbot):
    from src.models import Oferta
    o1 = Oferta(
        id_o=301, id_e=10, descripcion_oferta="Active Offer", requisitos="None", 
        fecha_de_publicacion="2026-06-01", duracion="3 meses", remuneracion=500.0, 
        validada_por_coordinador=True, activo=True
    )
    o2 = Oferta(
        id_o=302, id_e=10, descripcion_oferta="Inactive Offer", requisitos="None", 
        fecha_de_publicacion="2026-06-01", duracion="3 meses", remuneracion=500.0, 
        validada_por_coordinador=True, activo=False
    )

    mock_service = MagicMock()
    all_offers = [o1, o2]
    mock_service.obtener_catalogo_ofertas.side_effect = lambda x: [
        o for o in all_offers 
        if getattr(o, "validada_por_coordinador", False) is True and getattr(o, "activo", True) is True
    ]

    mock_profile = MagicMock(id_p=33, nombre_y_apellido="Estudiante", correo_electronico="estudiante@prueba.com")

    # We patch the repositories to prevent loading real data
    with (
        patch("src.controllers.estudiante_controller.EmpresaRepository"),
        patch("src.controllers.estudiante_controller.OfertaRepository"),
        patch("src.controllers.estudiante_controller.PostulacionRepository"),
        patch("src.controllers.estudiante_controller.ActividadRepository"),
    ):
        view = MainWindow_Estudiante()
        controller = EstudianteController(view, mock_service, mock_profile)
        qtbot.addWidget(view)

        # Initial catalog has only 1 active offer
        assert view.tblOfertasDisponibles.rowCount() == 1
        assert view.tblOfertasDisponibles.item(0, 0).text() == "Active Offer"

        # Mutate to inactive (activo = False) and reload
        o1.activo = False
        controller.cargar_ofertas()

        # The catalog must hide/remove it immediately
        assert view.tblOfertasDisponibles.rowCount() == 0

    # Verify stylesheet is set on views of different controllers
    with patch("PyQt6.QtWidgets.QMessageBox.critical"), \
         patch("PyQt6.QtWidgets.QMessageBox.warning"), \
         patch("PyQt6.QtWidgets.QMessageBox.information"):
        # 1. Login
        from src.controllers import LoginController
        from src.views import LoginWindow
        login_view = LoginWindow()
        _ = LoginController(login_view, MagicMock())
        assert login_view.styleSheet() != ""
        qtbot.addWidget(login_view)
        
        # 2. Coordinador
        from src.controllers import CoordinadorController
        from src.views import MainWindow_Coordinador
        coord_view = MainWindow_Coordinador()
        _ = CoordinadorController(coord_view, MagicMock(), MagicMock())
        assert coord_view.styleSheet() != ""
        qtbot.addWidget(coord_view)

        # 3. Empresa
        from src.controllers import EmpresaController
        from src.views import MainWindow_Empresa
        emp_view = MainWindow_Empresa()
        _ = EmpresaController(emp_view, MagicMock(), MagicMock())
        assert emp_view.styleSheet() != ""
        qtbot.addWidget(emp_view)

        # 4. Tutor Academico
        from src.controllers import TutorAcademicoController
        from src.views import MainWindow_TutorAcademico
        ta_view = MainWindow_TutorAcademico()
        _ = TutorAcademicoController(ta_view, MagicMock(), MagicMock())
        assert ta_view.styleSheet() != ""
        qtbot.addWidget(ta_view)

        # 5. Tutor Empresarial
        from src.controllers import TutorEmpresarialController
        from src.views import MainWindow_TutorEmpresarial
        te_view = MainWindow_TutorEmpresarial()
        _ = TutorEmpresarialController(te_view, MagicMock(), MagicMock())
        assert te_view.styleSheet() != ""
        qtbot.addWidget(te_view)

        # 6. Administrador
        from src.controllers import AdministradorController
        from src.views import MainWindow_Administrador
        admin_view = MainWindow_Administrador()
        _ = AdministradorController(admin_view, MagicMock())
        assert admin_view.styleSheet() != ""
        qtbot.addWidget(admin_view)

