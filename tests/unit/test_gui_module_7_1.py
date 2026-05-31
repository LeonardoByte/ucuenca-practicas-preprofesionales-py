from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMessageBox

from src.controllers import AdministradorController, LoginController, Router
from src.models.estados import EstadoMatricula, RolUsuario
from src.views import LoginWindow, MainWindow_Administrador


def test_login_validation_empty_email(qtbot):
    mock_service = MagicMock()
    view = LoginWindow()
    _controller = LoginController(view, mock_service)
    qtbot.addWidget(view)

    # Empty email
    view.txtCorreo.setText("")
    view.txtContrasena.setText("some_password")

    with patch("src.controllers.login_controller.QMessageBox.critical") as mock_critical:
        view.btnIngresar.click()
        mock_critical.assert_called_once_with(
            view, "Error de Validación", "Debe ingresar el correo electrónico."
        )


def test_login_validation_empty_password(qtbot):
    mock_service = MagicMock()
    view = LoginWindow()
    _controller = LoginController(view, mock_service)
    qtbot.addWidget(view)

    # Empty password
    view.txtCorreo.setText("maria.andrade@ucuenca.edu.ec")
    view.txtContrasena.setText("")

    with patch("src.controllers.login_controller.QMessageBox.critical") as mock_critical:
        view.btnIngresar.click()
        mock_critical.assert_called_once_with(
            view, "Error de Validación", "Debe ingresar la contraseña."
        )


def test_login_validation_invalid_email_format(qtbot):
    mock_service = MagicMock()
    view = LoginWindow()
    _controller = LoginController(view, mock_service)
    qtbot.addWidget(view)

    # Invalid email format (missing @ or domain)
    view.txtCorreo.setText("invalid_email")
    view.txtContrasena.setText("some_password")

    with patch("src.controllers.login_controller.QMessageBox.critical") as mock_critical:
        view.btnIngresar.click()
        mock_critical.assert_called_once_with(
            view, "Error de Validación", "El correo electrónico no tiene un formato válido."
        )


def test_login_success_emits_signal(qtbot):
    mock_service = MagicMock()
    dummy_profile = MagicMock()
    mock_service.ejecutar_ingreso.return_value = (dummy_profile, RolUsuario.ADMINISTRADOR)

    view = LoginWindow()
    controller = LoginController(view, mock_service)
    qtbot.addWidget(view)

    view.txtCorreo.setText("admin@ucuenca.edu.ec")
    view.txtContrasena.setText("admin123")

    spy = MagicMock()
    controller.login_exitoso.connect(spy)

    view.btnIngresar.click()

    mock_service.ejecutar_ingreso.assert_called_once_with("admin@ucuenca.edu.ec", "admin123")
    spy.assert_called_once_with(dummy_profile, RolUsuario.ADMINISTRADOR)


def test_router_workflow(qtbot):
    mock_services = {
        "login_service": MagicMock(),
        "administrador_service": MagicMock(),
    }

    # We can use the actual views for testing integration!
    view_factories = {
        "LoginWindow": lambda: LoginWindow(),
        RolUsuario.ADMINISTRADOR: lambda: MainWindow_Administrador(),
    }

    router = Router(mock_services, view_factories)

    with patch("src.controllers.login_controller.QMessageBox.critical"), \
         patch("src.controllers.administrador_controller.QMessageBox.critical"):
        router.start()

        login_view = router.current_view
        qtbot.addWidget(login_view)

        # Verify login view is shown
        assert login_view.isVisible()

        # Now simulate login success signal
        dummy_profile = MagicMock()

        router.current_controller.login_exitoso.emit(dummy_profile, RolUsuario.ADMINISTRADOR)

        # Verify LoginWindow is closed/hidden
        assert not login_view.isVisible()

        # Verify MainWindow_Administrador is shown
        admin_view = router.current_view
        qtbot.addWidget(admin_view)
        assert admin_view.isVisible()


def test_admin_navigation_sidebar_and_menubar(qtbot):
    mock_service = MagicMock()
    mock_service.obtener_todos_los_usuarios_sistema.return_value = []
    view = MainWindow_Administrador()
    _controller = AdministradorController(view, mock_service)
    qtbot.addWidget(view)

    # Default page index should be 0
    assert view.stackedWidgetCentral.currentIndex() == 0

    # Nav to Auditoria
    view.btnNavEliminarUsuario.click()
    assert view.stackedWidgetCentral.currentIndex() == 1

    # Nav to Registro
    view.btnNavIngresarUsuario.click()
    assert view.stackedWidgetCentral.currentIndex() == 0

    # Trigger trigger registrar from action
    view.actAuditoriaUsuarios.trigger()
    assert view.stackedWidgetCentral.currentIndex() == 1

    # Trigger trigger auditoria from action
    view.actRegistrarUsuario.trigger()
    assert view.stackedWidgetCentral.currentIndex() == 0


def test_admin_polymorphic_form_switching(qtbot):
    mock_service = MagicMock()
    mock_service.obtener_todos_los_usuarios_sistema.return_value = []
    view = MainWindow_Administrador()
    _controller = AdministradorController(view, mock_service)
    qtbot.addWidget(view)

    # Estudiante -> stackedWidgetFormularios index 0
    view.cmbTipoUsuario.setCurrentIndex(0)
    assert view.stackedWidgetFormularios.currentIndex() == 0

    # Coordinador -> index 1
    view.cmbTipoUsuario.setCurrentIndex(1)
    assert view.stackedWidgetFormularios.currentIndex() == 1

    # Tutor Academico -> index 1
    view.cmbTipoUsuario.setCurrentIndex(2)
    assert view.stackedWidgetFormularios.currentIndex() == 1

    # Tutor Empresarial -> index 2
    view.cmbTipoUsuario.setCurrentIndex(3)
    assert view.stackedWidgetFormularios.currentIndex() == 2

    # Administrador -> index 1
    view.cmbTipoUsuario.setCurrentIndex(4)
    assert view.stackedWidgetFormularios.currentIndex() == 1

    # Empresa -> index 3
    view.cmbTipoUsuario.setCurrentIndex(5)
    assert view.stackedWidgetFormularios.currentIndex() == 3


def test_admin_reactive_filtering(qtbot):
    mock_service = MagicMock()
    mock_service.obtener_todos_los_usuarios_sistema.return_value = [
        {
            "username_correo": "maria.andrade@ucuenca.edu.ec",
            "rol": RolUsuario.ESTUDIANTE,
            "id_p": 1,
        },
        {
            "username_correo": "pedro.sarmiento@ucuenca.edu.ec",
            "rol": RolUsuario.COORDINADOR,
            "id_p": 2,
        },
    ]
    view = MainWindow_Administrador()
    _controller = AdministradorController(view, mock_service)
    qtbot.addWidget(view)

    # Initial state: both rows visible
    assert not view.tableWidget.isRowHidden(0)
    assert not view.tableWidget.isRowHidden(1)

    # Type "maria" -> only first row visible
    view.txtBusquedaCorreo.setText("maria")
    assert not view.tableWidget.isRowHidden(0)
    assert view.tableWidget.isRowHidden(1)

    # Clear filter -> both visible
    view.txtBusquedaCorreo.clear()
    assert not view.tableWidget.isRowHidden(0)
    assert not view.tableWidget.isRowHidden(1)


def test_admin_create_student_success(qtbot):
    mock_service = MagicMock()
    mock_service.obtener_todos_los_usuarios_sistema.return_value = []
    view = MainWindow_Administrador()
    _controller = AdministradorController(view, mock_service)
    qtbot.addWidget(view)

    # Fill Student details
    view.cmbTipoUsuario.setCurrentIndex(0) # Estudiante
    view.txtEstudianteNombre.setText("Maria Andrade")
    view.txtEstudianteCedula.setText("0102030405")
    view.txtEstudianteCorreo.setText("maria.andrade@ucuenca.edu.ec")
    view.txtEstudianteDireccion.setText("Cuenca")
    view.sbxEstudianteCiclo.setValue(5)
    view.comboBox.setCurrentIndex(0) # "Matriculado"

    mock_service.crear_cuenta_usuario_sistema.return_value = MagicMock()

    with patch("src.controllers.administrador_controller.QMessageBox.information") as mock_info:
        view.btnCrearUsuario.click()
        mock_service.crear_cuenta_usuario_sistema.assert_called_once_with(
            "maria.andrade@ucuenca.edu.ec",
            "password",
            RolUsuario.ESTUDIANTE,
            {
                "nombre_y_apellido": "Maria Andrade",
                "cedula_dni": "0102030405",
                "direccion": "Cuenca",
                "ciclo_actual": 5,
                "estado_de_matricula": EstadoMatricula.MATRICULADO,
            }
        )
        mock_info.assert_called_once_with(
            view, "Registro exitoso", "La información fue guardada correctamente."
        )


def test_admin_delete_user_workflow(qtbot):
    mock_service = MagicMock()
    mock_service.obtener_todos_los_usuarios_sistema.return_value = [
        {"username_correo": "admin@ucuenca.edu.ec", "rol": RolUsuario.ADMINISTRADOR, "id_p": 1}
    ]
    view = MainWindow_Administrador()
    _controller = AdministradorController(view, mock_service)
    qtbot.addWidget(view)

    # Verify user is loaded in table
    assert view.tableWidget.rowCount() == 1
    assert view.tableWidget.item(0, 0).text() == "admin@ucuenca.edu.ec"

    # 1. Try to delete without selection -> should show warning
    view.tableWidget.clearSelection()
    with patch("src.controllers.administrador_controller.QMessageBox.warning") as mock_warning:
        view.btnEliminarUsuario.click()
        mock_warning.assert_called_once_with(
            view, "Selección requerida", "Debe seleccionar un usuario de la tabla."
        )

    # 2. Select the row and click delete -> Cancel (No)
    view.tableWidget.selectRow(0)
    mock_service.eliminar_usuario_sistema.reset_mock()
    with patch(
        "src.controllers.administrador_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.No,
    ) as mock_question:
        view.btnEliminarUsuario.click()
        mock_question.assert_called_once()
        mock_service.eliminar_usuario_sistema.assert_not_called()

    # 3. Select the row and click delete -> Confirm (Yes)
    mock_service.eliminar_usuario_sistema.return_value = True
    with patch(
        "src.controllers.administrador_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes,
    ) as mock_question, patch(
        "src.controllers.administrador_controller.QMessageBox.information"
    ) as mock_info:
        view.btnEliminarUsuario.click()
        mock_question.assert_called_once()
        mock_service.eliminar_usuario_sistema.assert_called_once_with("admin@ucuenca.edu.ec")
        mock_info.assert_called_once_with(
            view, "Baja exitosa", "El usuario fue eliminado correctamente."
        )


def test_admin_logout_workflow(qtbot):
    mock_service = MagicMock()
    mock_service.obtener_todos_los_usuarios_sistema.return_value = []
    view = MainWindow_Administrador()
    controller = AdministradorController(view, mock_service)
    qtbot.addWidget(view)

    spy = MagicMock()
    controller.cerrar_sesion.connect(spy)

    # 1. Click Cerrar Sesion button -> Cancel (No)
    with patch(
        "src.controllers.administrador_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.No,
    ) as mock_question:
        view.btnNavCerrarSesion.click()
        mock_question.assert_called_once()
        spy.assert_not_called()

    # 2. Click Cerrar Sesion button -> Confirm (Yes)
    with patch(
        "src.controllers.administrador_controller.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Yes,
    ) as mock_question:
        view.btnNavCerrarSesion.click()
        mock_question.assert_called_once()
        spy.assert_called_once()


def test_admin_help_dialogs(qtbot):
    mock_service = MagicMock()
    mock_service.obtener_todos_los_usuarios_sistema.return_value = []
    view = MainWindow_Administrador()
    _controller = AdministradorController(view, mock_service)
    qtbot.addWidget(view)

    # We will intercept QDialog.exec and track which index was shown
    dialog_instances = []
    def mock_exec_func(self):
        dialog_instances.append(self)
        return 1

    with patch("PyQt6.QtWidgets.QDialog.exec", mock_exec_func):
        # 1. actAcercaPrograma -> index 0
        view.actAcercaPrograma.trigger()
        assert len(dialog_instances) == 1
        assert dialog_instances[-1].stackedWidgetAyuda.currentIndex() == 0

        # 2. actAcercaDesarrollador -> index 1
        view.actAcercaDesarrollador.trigger()
        assert len(dialog_instances) == 2
        assert dialog_instances[-1].stackedWidgetAyuda.currentIndex() == 1

        # 3. actRepositorioGithub -> index 2
        with patch("PyQt6.QtGui.QDesktopServices.openUrl") as mock_open_url:
            view.actRepositorioGithub.trigger()
            assert len(dialog_instances) == 3
            assert dialog_instances[-1].stackedWidgetAyuda.currentIndex() == 2
            mock_open_url.assert_called_once_with(QUrl("https://github.com/LeonardoByte"))
