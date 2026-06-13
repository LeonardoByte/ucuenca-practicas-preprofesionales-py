import json
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QMessageBox

from src.controllers import CoordinadorController
from src.models.estados import EstadoPostulacion, EstadoPractica
from src.services.exceptions import DocumentacionIncompletaError
from src.views import MainWindow_Coordinador


def setup_coordinador_test():
    mock_service = MagicMock()
    mock_coordinador_perfil = MagicMock()
    mock_coordinador_perfil.id_p = 5

    # Mock repos
    mock_empresa_repo = MagicMock()
    mock_tutor_acad_repo = MagicMock()
    mock_estudiante_repo = MagicMock()
    mock_tutor_emp_repo = MagicMock()

    # Stub searches
    # Estudiante
    est1 = MagicMock(
        id_p=1, nombre_y_apellido="Estudiante Uno", correo_electronico="uno@student.com"
    )
    est2 = MagicMock(
        id_p=2, nombre_y_apellido="Estudiante Dos", correo_electronico="dos@student.com"
    )
    est_map = {1: est1, 2: est2}
    mock_estudiante_repo.buscar_por_id.side_effect = lambda x: est_map.get(x)

    # Empresa
    emp1 = MagicMock(id_e=10, nombre_empresa="Empresa Uno")
    emp2 = MagicMock(id_e=20, nombre_empresa="Empresa Dos")
    emp_map = {10: emp1, 20: emp2}
    mock_empresa_repo.buscar_por_id.side_effect = lambda x: emp_map.get(x)

    # Tutor Academico
    t_acad1 = MagicMock(id_p=30, nombre_y_apellido="Tutor Acad Uno")
    t_acad2 = MagicMock(id_p=40, nombre_y_apellido="Tutor Acad Dos")
    t_acad_map = {30: t_acad1, 40: t_acad2}
    mock_tutor_acad_repo.buscar_por_id.side_effect = lambda x: t_acad_map.get(x)
    mock_tutor_acad_repo.obtener_todos.return_value = [t_acad1, t_acad2]

    # Tutor Empresarial
    t_emp1 = MagicMock(id_p=50, nombre_y_apellido="Tutor Emp Uno")
    t_emp2 = MagicMock(id_p=60, nombre_y_apellido="Tutor Emp Dos")
    t_emp_map = {50: t_emp1, 60: t_emp2}
    mock_tutor_emp_repo.buscar_por_id.side_effect = lambda x: t_emp_map.get(x)

    # Oferta mock search on service.oferta_repo
    mock_oferta_repo = MagicMock()
    oferta1 = MagicMock(
        id_o=100, id_e=10, descripcion_oferta=json.dumps({"titulo": "Developer Python"})
    )
    oferta2 = MagicMock(id_o=200, id_e=20, descripcion_oferta="Plain text offer description")
    oferta_map = {100: oferta1, 200: oferta2}
    mock_oferta_repo.buscar_por_id.side_effect = lambda x: oferta_map.get(x)
    mock_service.oferta_repo = mock_oferta_repo

    # Mock service methods
    # Page 1: Postulaciones and count
    p1 = MagicMock(id_pos=11, id_p_estudiante=1, id_e=10, id_o=100, fecha_postulacion="2026-06-01")
    p2 = MagicMock(id_pos=12, id_p_estudiante=2, id_e=20, id_o=200, fecha_postulacion="2026-06-02")
    mock_service.revisar_postulaciones_pendientes.return_value = [p1, p2]

    o_count1 = {
        "id_e": 10,
        "id_o": 100,
        "descripcion_oferta": json.dumps({"titulo": "Developer Python"}),
        "conteo_validadas": 3,
    }
    o_count2 = {
        "id_e": 20,
        "id_o": 200,
        "descripcion_oferta": "Plain text offer description",
        "conteo_validadas": 1,
    }
    mock_service.listar_ofertas_con_conteo_validadas.return_value = [o_count1, o_count2]

    # Page 2: Practicas sin tutor
    pr_sin1 = MagicMock(id_pr=1001, id_pos=11, fecha_inicio="2026-06-05")
    mock_service.listar_practicas_pendientes_de_tutor.return_value = [pr_sin1]

    # Page 3: Solicitudes
    auth_sol1 = MagicMock(
        id_p_estudiante=1,
        id_sol_aut=301,
        nombre_empresa="Empresa Uno",
        detalles_empresa="Autorizacion 1",
        fecha_solicitud="2026-06-03",
    )
    of_sol1 = MagicMock(
        id_p_estudiante=2, id_sol_of=401, nombre_destinatario="Dest 1", nombre_empresa="Empresa Dos"
    )
    mock_service.listar_solicitudes_autorizacion_pendientes.return_value = [auth_sol1]
    mock_service.listar_solicitudes_oficio_pendientes.return_value = [of_sol1]

    # Page 4: Practicas activas
    pr_act1 = MagicMock(
        id_pr=2001,
        id_pos=11,
        id_p_tutor_acad=30,
        id_p_tutor_emp=50,
        fecha_inicio="2026-06-01",
        fecha_fin="2026-12-01",
        estado_de_practica=EstadoPractica.INICIADA,
    )
    mock_service.practica_repo._datos = [pr_act1]
    mock_service.postulacion_repo = MagicMock()
    mock_service.postulacion_repo.buscar_por_id.return_value = p1

    return {
        "service": mock_service,
        "coordinador_perfil": mock_coordinador_perfil,
        "empresa_repo": mock_empresa_repo,
        "tutor_acad_repo": mock_tutor_acad_repo,
        "estudiante_repo": mock_estudiante_repo,
        "tutor_emp_repo": mock_tutor_emp_repo,
    }


def test_coordinador_navigation_sidebar_and_menubar(qtbot):
    mocks = setup_coordinador_test()

    with (
        patch(
            "src.controllers.coordinador_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorAcademicoRepository",
            return_value=mocks["tutor_acad_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.EstudianteRepository",
            return_value=mocks["estudiante_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorEmpresarialRepository",
            return_value=mocks["tutor_emp_repo"],
        ),
    ):
        view = MainWindow_Coordinador()
        _controller = CoordinadorController(view, mocks["service"], mocks["coordinador_perfil"])
        qtbot.addWidget(view)

        # Default page index is 0 (Postulaciones)
        assert view.stackedWidgetCentral.currentIndex() == 0

        # Sidebar navigation
        view.btnNavAsignaciones.click()
        assert view.stackedWidgetCentral.currentIndex() == 2

        view.btnNavSolicitudes.click()
        assert view.stackedWidgetCentral.currentIndex() == 3

        view.btnNavCierre.click()
        assert view.stackedWidgetCentral.currentIndex() == 4

        view.btnNavPostulaciones.click()
        assert view.stackedWidgetCentral.currentIndex() == 0

        # Menubar trigger actions
        view.actAsignarTutores.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 2

        view.actAutorizacionesPendientes.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 3

        view.actCierreOficial.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 4

        view.actRevisarPostulaciones.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 0

        view.actGenerarTernas.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 0

        view.actEmitirOficios.trigger()
        assert view.stackedWidgetCentral.currentIndex() == 3


def test_coordinador_postulaciones_loading_and_actions(qtbot):
    mocks = setup_coordinador_test()

    with (
        patch(
            "src.controllers.coordinador_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorAcademicoRepository",
            return_value=mocks["tutor_acad_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.EstudianteRepository",
            return_value=mocks["estudiante_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorEmpresarialRepository",
            return_value=mocks["tutor_emp_repo"],
        ),
    ):
        view = MainWindow_Coordinador()
        _controller = CoordinadorController(view, mocks["service"], mocks["coordinador_perfil"])
        qtbot.addWidget(view)

        # 1. Row count and columns for Postulaciones
        assert view.tblPostulacionesPendientes.rowCount() == 2
        # Row 0: Student 1 (uno@student.com, Estudiante Uno, Empresa Uno, Dev Python)
        assert view.tblPostulacionesPendientes.item(0, 0).text() == "uno@student.com"
        assert view.tblPostulacionesPendientes.item(0, 1).text() == "Estudiante Uno"
        assert view.tblPostulacionesPendientes.item(0, 2).text() == "Empresa Uno"
        assert view.tblPostulacionesPendientes.item(0, 3).text() == "Developer Python"
        assert view.tblPostulacionesPendientes.item(0, 4).text() == "2026-06-01"

        # UserRole data contains postulation ID (11)
        assert view.tblPostulacionesPendientes.item(0, 0).data(Qt.ItemDataRole.UserRole) == 11

        # 2. Row count and columns for Ofertas Conteo
        assert view.tblOfertasConteo.rowCount() == 2
        assert view.tblOfertasConteo.item(0, 0).text() == "100"
        assert view.tblOfertasConteo.item(0, 1).text() == "Empresa Uno"
        assert view.tblOfertasConteo.item(0, 2).text() == "Developer Python"
        assert view.tblOfertasConteo.item(0, 3).text() == "3"

        # 3. Validation action without selection -> warning
        view.tblPostulacionesPendientes.clearSelection()
        with patch("src.controllers.coordinador_controller.QMessageBox.warning") as mock_warn:
            view.btnValidarPostulacion.click()
            mock_warn.assert_called_once_with(
                view, "Selección requerida", "Debe seleccionar una postulación."
            )

        # 4. Validar postulación (Yes)
        view.tblPostulacionesPendientes.selectRow(0)
        mocks["service"].validar_requisitos_alumno.return_value = True

        with (
            patch(
                "src.controllers.coordinador_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info,
        ):
            view.btnValidarPostulacion.click()
            mocks["service"].validar_requisitos_alumno.assert_called_once_with(11, True)
            mock_info.assert_called_once()

        # 5. Rechazar postulación (No / Yes)
        mocks["service"].validar_requisitos_alumno.reset_mock()
        view.tblPostulacionesPendientes.selectRow(0)

        with patch(
            "src.controllers.coordinador_controller.QMessageBox.question",
            return_value=QMessageBox.StandardButton.No,
        ):
            view.btnRechazarPostulacion.click()
            mocks["service"].validar_requisitos_alumno.assert_not_called()

        with (
            patch(
                "src.controllers.coordinador_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info,
        ):
            view.btnRechazarPostulacion.click()
            mocks["service"].validar_requisitos_alumno.assert_called_once_with(11, False)


def test_coordinador_conteo_terna_activation_and_submit(qtbot):
    mocks = setup_coordinador_test()

    with (
        patch(
            "src.controllers.coordinador_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorAcademicoRepository",
            return_value=mocks["tutor_acad_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.EstudianteRepository",
            return_value=mocks["estudiante_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorEmpresarialRepository",
            return_value=mocks["tutor_emp_repo"],
        ),
    ):
        view = MainWindow_Coordinador()
        _controller = CoordinadorController(view, mocks["service"], mocks["coordinador_perfil"])
        qtbot.addWidget(view)

        # Initially button is disabled
        assert not view.btnEnviarTerna.isEnabled()

        # Selection changes to row 1 (conteo = 1) -> enabled (as 3-candidate restriction is removed)
        view.tblOfertasConteo.selectRow(1)
        assert view.btnEnviarTerna.isEnabled()

        # Selection changes to row 0 (conteo = 3) -> enabled
        view.tblOfertasConteo.selectRow(0)
        assert view.btnEnviarTerna.isEnabled()

        # 1. Generar terna (No)
        with patch(
            "src.controllers.coordinador_controller.QMessageBox.question",
            return_value=QMessageBox.StandardButton.No,
        ):
            view.btnEnviarTerna.click()
            mocks["service"].enviar_terna_a_empresa.assert_not_called()

        # 2. Generar terna (Yes)
        # Mock some postulations inside repo to retrieve
        p_val1 = MagicMock(id_pos=51, id_o=100, estado_de_postulacion=EstadoPostulacion.VALIDADA)
        p_val2 = MagicMock(id_pos=52, id_o=100, estado_de_postulacion=EstadoPostulacion.VALIDADA)
        p_val3 = MagicMock(id_pos=53, id_o=100, estado_de_postulacion=EstadoPostulacion.VALIDADA)
        mocks["service"].postulacion_repo._datos = [p_val1, p_val2, p_val3]
        mocks["service"].enviar_terna_a_empresa.return_value = True

        with (
            patch(
                "src.controllers.coordinador_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info,
        ):
            view.btnEnviarTerna.click()
            mocks["service"].enviar_terna_a_empresa.assert_called_once_with([51, 52, 53])
            mock_info.assert_called_once()


def test_coordinador_asignacion_tutores(qtbot):
    mocks = setup_coordinador_test()

    with (
        patch(
            "src.controllers.coordinador_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorAcademicoRepository",
            return_value=mocks["tutor_acad_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.EstudianteRepository",
            return_value=mocks["estudiante_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorEmpresarialRepository",
            return_value=mocks["tutor_emp_repo"],
        ),
    ):
        view = MainWindow_Coordinador()
        _controller = CoordinadorController(view, mocks["service"], mocks["coordinador_perfil"])
        qtbot.addWidget(view)

        view.btnNavAsignaciones.click()

        # 1. Verify table loading
        assert view.tblPracticasSinTutor.rowCount() == 1
        assert view.tblPracticasSinTutor.item(0, 0).text() == "1001"
        assert (
            view.tblPracticasSinTutor.item(0, 1).text() == "uno@student.com"
        )  # Email is in the second column!
        assert view.tblPracticasSinTutor.item(0, 2).text() == "Estudiante Uno"
        assert view.tblPracticasSinTutor.item(0, 3).text() == "Empresa Uno"
        assert view.tblPracticasSinTutor.item(0, 4).text() == "2026-06-05"

        # 2. Verify tutores combo loading
        assert view.cmbTutoresDisponibles.count() == 2
        assert view.cmbTutoresDisponibles.itemText(0) == "Tutor Acad Uno"
        assert view.cmbTutoresDisponibles.itemData(0) == 30
        assert view.cmbTutoresDisponibles.itemText(1) == "Tutor Acad Dos"
        assert view.cmbTutoresDisponibles.itemData(1) == 40

        # 3. Assign tutor without selection -> warning
        view.tblPracticasSinTutor.clearSelection()
        with patch("src.controllers.coordinador_controller.QMessageBox.warning") as mock_warn:
            view.btnAsignarTutor.click()
            mock_warn.assert_called_once_with(
                view, "Selección requerida", "Debe seleccionar una práctica de la tabla."
            )

        # 4. Assign tutor (Yes)
        view.tblPracticasSinTutor.selectRow(0)
        view.cmbTutoresDisponibles.setCurrentIndex(1)  # Tutor Acad Dos (40)
        mocks["service"].asignar_tutor_a_practica.return_value = True

        with (
            patch(
                "src.controllers.coordinador_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info,
        ):
            view.btnAsignarTutor.click()
            mocks["service"].asignar_tutor_a_practica.assert_called_once_with(1001, 40)
            mock_info.assert_called_once()


def test_coordinador_solicitudes_and_oficios(qtbot):
    mocks = setup_coordinador_test()

    with (
        patch(
            "src.controllers.coordinador_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorAcademicoRepository",
            return_value=mocks["tutor_acad_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.EstudianteRepository",
            return_value=mocks["estudiante_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorEmpresarialRepository",
            return_value=mocks["tutor_emp_repo"],
        ),
    ):
        view = MainWindow_Coordinador()
        _controller = CoordinadorController(view, mocks["service"], mocks["coordinador_perfil"])
        qtbot.addWidget(view)

        view.btnNavSolicitudes.click()

        # 1. Verify Table Solicitudes
        assert view.tblAutorizacionesPendientes.rowCount() == 1
        assert view.tblAutorizacionesPendientes.item(0, 0).text() == "Estudiante Uno"
        assert view.tblAutorizacionesPendientes.item(0, 0).data(Qt.ItemDataRole.UserRole) == 301
        assert view.tblAutorizacionesPendientes.item(0, 1).text() == "Empresa Uno"
        assert view.tblAutorizacionesPendientes.item(0, 2).text() == "Autorizacion 1"
        assert view.tblAutorizacionesPendientes.item(0, 3).text() == "2026-06-03"

        # 2. Verify Table Oficios
        assert view.tblOficiosPendientes.rowCount() == 1
        assert view.tblOficiosPendientes.item(0, 0).text() == "Estudiante Dos"
        assert view.tblOficiosPendientes.item(0, 0).data(Qt.ItemDataRole.UserRole) == 401
        assert view.tblOficiosPendientes.item(0, 1).text() == "Dest 1"
        assert view.tblOficiosPendientes.item(0, 2).text() == "Empresa Dos"

        # 3. Approve authorization request
        view.tblAutorizacionesPendientes.selectRow(0)
        mocks["service"].evaluar_solicitud_autorizacion.return_value = True

        with (
            patch(
                "src.controllers.coordinador_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info,
        ):
            view.btnAprobarAutorizacion.click()
            mocks["service"].evaluar_solicitud_autorizacion.assert_called_once_with(
                301, True, 5, "Representante", "Director"
            )
            mock_info.assert_called_once()

        # 4. Reject authorization request
        mocks["service"].evaluar_solicitud_autorizacion.reset_mock()
        view.tblAutorizacionesPendientes.selectRow(0)

        with (
            patch(
                "src.controllers.coordinador_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info,
        ):
            view.btnRechazarAutorizacion.click()
            mocks["service"].evaluar_solicitud_autorizacion.assert_called_once_with(
                301, False, 5, "Representante", "Director"
            )

        # 5. Process Oficio
        view.tblOficiosPendientes.selectRow(0)
        mocks["service"].procesar_emision_oficio.return_value = True

        # Resolve pushButton/btnProcesarOficio dynamically
        btn_oficio = getattr(view, "btnProcesarOficio", getattr(view, "pushButton", None))
        assert btn_oficio is not None

        with (
            patch(
                "src.controllers.coordinador_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info,
        ):
            btn_oficio.click()
            mocks["service"].procesar_emision_oficio.assert_called_once_with(
                401, 5, "oficio_emitido.pdf"
            )
            mock_info.assert_called_once()


def test_coordinador_cierre_oficial_and_zero_trust(qtbot):
    mocks = setup_coordinador_test()

    with (
        patch(
            "src.controllers.coordinador_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorAcademicoRepository",
            return_value=mocks["tutor_acad_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.EstudianteRepository",
            return_value=mocks["estudiante_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorEmpresarialRepository",
            return_value=mocks["tutor_emp_repo"],
        ),
    ):
        view = MainWindow_Coordinador()
        _controller = CoordinadorController(view, mocks["service"], mocks["coordinador_perfil"])
        qtbot.addWidget(view)

        view.btnNavCierre.click()

        # 1. Table Practicas Activas loaded correctly
        assert view.tblPracticasActivas.rowCount() == 1
        assert view.tblPracticasActivas.item(0, 0).text() == "Estudiante Uno"
        assert view.tblPracticasActivas.item(0, 0).data(Qt.ItemDataRole.UserRole) == 2001
        assert view.tblPracticasActivas.item(0, 1).text() == "Tutor Acad Uno"
        assert view.tblPracticasActivas.item(0, 2).text() == "Tutor Emp Uno"
        assert view.tblPracticasActivas.item(0, 3).text() == "2026-06-01"
        assert view.tblPracticasActivas.item(0, 4).text() == "2026-12-01"

        # 2. Execute closure without selection -> warning
        view.tblPracticasActivas.clearSelection()
        with patch("src.controllers.coordinador_controller.QMessageBox.warning") as mock_warn:
            view.btnEjecutarCierre.click()
            mock_warn.assert_called_once_with(
                view, "Selección requerida", "Por favor, seleccione una práctica."
            )

        # 3. Execute closure zero-trust failure -> QMessageBox.critical
        view.tblPracticasActivas.selectRow(0)
        mocks[
            "service"
        ].ejecutar_cierre_oficial_practica.side_effect = DocumentacionIncompletaError(
            "Faltan firmas en el Formulario 2."
        )

        with (
            patch(
                "src.controllers.coordinador_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.coordinador_controller.QMessageBox.critical") as mock_crit,
        ):
            view.btnEjecutarCierre.click()
            mocks["service"].ejecutar_cierre_oficial_practica.assert_called_once_with(2001)
            mock_crit.assert_called_once_with(
                view, "Error de Documentación", "Faltan firmas en el Formulario 2."
            )

        # 4. Execute closure success -> QMessageBox.information
        mocks["service"].ejecutar_cierre_oficial_practica.reset_mock()
        mocks["service"].ejecutar_cierre_oficial_practica.side_effect = None
        mocks["service"].ejecutar_cierre_oficial_practica.return_value = True

        with (
            patch(
                "src.controllers.coordinador_controller.QMessageBox.question",
                return_value=QMessageBox.StandardButton.Yes,
            ),
            patch("src.controllers.coordinador_controller.QMessageBox.information") as mock_info,
        ):
            view.btnEjecutarCierre.click()
            mocks["service"].ejecutar_cierre_oficial_practica.assert_called_once_with(2001)
            mock_info.assert_called_once()


def test_coordinador_global_table_settings(qtbot):
    mocks = setup_coordinador_test()

    with (
        patch(
            "src.controllers.coordinador_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorAcademicoRepository",
            return_value=mocks["tutor_acad_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.EstudianteRepository",
            return_value=mocks["estudiante_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorEmpresarialRepository",
            return_value=mocks["tutor_emp_repo"],
        ),
    ):
        view = MainWindow_Coordinador()
        _controller = CoordinadorController(view, mocks["service"], mocks["coordinador_perfil"])
        qtbot.addWidget(view)

        tablas = [
            view.tblPostulacionesPendientes,
            view.tblOfertasConteo,
            view.tblPracticasSinTutor,
            view.tblAutorizacionesPendientes,
            view.tblOficiosPendientes,
            view.tblPracticasActivas,
        ]

        from PyQt6.QtWidgets import QAbstractItemView

        for tbl in tablas:
            assert tbl.editTriggers() == QAbstractItemView.EditTrigger.NoEditTriggers
            assert tbl.selectionBehavior() == QAbstractItemView.SelectionBehavior.SelectRows
            assert tbl.selectionMode() == QAbstractItemView.SelectionMode.SingleSelection


def test_coordinador_logout_and_help_dialogs(qtbot):
    mocks = setup_coordinador_test()

    with (
        patch(
            "src.controllers.coordinador_controller.EmpresaRepository",
            return_value=mocks["empresa_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorAcademicoRepository",
            return_value=mocks["tutor_acad_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.EstudianteRepository",
            return_value=mocks["estudiante_repo"],
        ),
        patch(
            "src.controllers.coordinador_controller.TutorEmpresarialRepository",
            return_value=mocks["tutor_emp_repo"],
        ),
    ):
        view = MainWindow_Coordinador()
        controller = CoordinadorController(view, mocks["service"], mocks["coordinador_perfil"])
        qtbot.addWidget(view)

        # Logout Cancel
        spy = MagicMock()
        controller.cerrar_sesion.connect(spy)

        with patch(
            "src.controllers.coordinador_controller.QMessageBox.question",
            return_value=QMessageBox.StandardButton.No,
        ):
            view.btnNavCerrarSesion.click()
            spy.assert_not_called()

        # Logout Confirm
        with patch(
            "src.controllers.coordinador_controller.QMessageBox.question",
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
