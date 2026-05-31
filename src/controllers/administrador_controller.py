import re

from PyQt6 import uic
from PyQt6.QtCore import QObject, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from src.models.estados import EstadoConvenio, EstadoMatricula, RolUsuario
from src.services.interfaces.administrador_main_service_abc import AdministradorMainServiceABC


class AdministradorController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: AdministradorMainServiceABC) -> None:
        super().__init__()
        self.view = view
        self.service = service

        # Load the dynamic UI
        uic.loadUi("src/views/ui/main_window_administrador.ui", self.view)

        # Alias for tblUsuarios
        self.view.tblUsuarios = self.view.tableWidget

        # Navigation connections (Sidebar buttons)
        self.view.btnNavIngresarUsuario.clicked.connect(self.ir_a_ingresar_usuario)
        self.view.btnNavEliminarUsuario.clicked.connect(self.ir_a_auditoria)
        self.view.btnNavCerrarSesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Menubar action connections
        self.view.actRegistrarUsuario.triggered.connect(self.ir_a_ingresar_usuario)
        self.view.actAuditoriaUsuarios.triggered.connect(self.ir_a_auditoria)
        self.view.actCerrarSesion.triggered.connect(self.solicitar_cerrar_sesion)
        self.view.actSalirSistema.triggered.connect(self.salir_sistema)

        # Help menu action connections
        self.view.actAcercaPrograma.triggered.connect(self.mostrar_acerca_programa)
        self.view.actAcercaDesarrollador.triggered.connect(self.mostrar_acerca_desarrollador)
        self.view.actRepositorioGithub.triggered.connect(self.mostrar_repositorio_github)

        # Action buttons
        self.view.btnCrearUsuario.clicked.connect(self.crear_usuario)
        self.view.btnEliminarUsuario.clicked.connect(self.eliminar_usuario)

        # Polymorphic dynamic form switching
        self.view.cmbTipoUsuario.currentIndexChanged.connect(self.alternar_formulario_rol)

        # Reactive real-time filter
        self.view.txtBusquedaCorreo.textChanged.connect(self.filtrar_usuarios)

        # Initial setups
        self.view.stackedWidgetCentral.setCurrentIndex(0)
        self.view.cmbTipoUsuario.setCurrentIndex(0)
        self.view.stackedWidgetFormularios.setCurrentIndex(0)

        self.cargar_empresas()
        self.cargar_usuarios()

    def ir_a_ingresar_usuario(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(0)

    def ir_a_auditoria(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(1)
        self.cargar_usuarios()

    def solicitar_cerrar_sesion(self) -> None:
        confirm = QMessageBox.question(
            self.view,
            "Confirmar Cierre de Sesión",
            "¿Está seguro de cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.cerrar_sesion.emit()

    def salir_sistema(self) -> None:
        confirm = QMessageBox.question(
            self.view,
            "Salir del Sistema",
            "¿Está seguro que desea salir del sistema?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.view.close()

    def alternar_formulario_rol(self, index: int) -> None:
        mapping = {
            0: 0,  # Estudiante -> page_3
            1: 1,  # Coordinador -> page_4
            2: 1,  # Tutor Academico -> page_4
            3: 2,  # Tutor Empresarial -> page_5
            4: 1,  # Administrador -> page_4
            5: 3,  # Empresa -> page_6
        }
        self.view.stackedWidgetFormularios.setCurrentIndex(mapping.get(index, 0))

    def cargar_empresas(self) -> None:
        try:
            self.view.cmbTutorEmpEmpresa.clear()
            # Retrieve directly from authenticationservice's empresa_repo
            if hasattr(self.service, "autenticacion_service"):
                empresas = self.service.autenticacion_service.empresa_repo.obtener_todos()
                for emp in empresas:
                    self.view.cmbTutorEmpEmpresa.addItem(emp.nombre_empresa, emp.id_e)
        except Exception:
            pass

    def cargar_usuarios(self) -> None:
        try:
            usuarios = self.service.obtener_todos_los_usuarios_sistema()
            self.view.tableWidget.setRowCount(0)
            for u in usuarios:
                row = self.view.tableWidget.rowCount()
                self.view.tableWidget.insertRow(row)
                self.view.tableWidget.setItem(row, 0, QTableWidgetItem(u["username_correo"]))
                # Convert RolUsuario to display string or print it
                rol_val = u["rol"].value if hasattr(u["rol"], "value") else str(u["rol"])
                self.view.tableWidget.setItem(row, 1, QTableWidgetItem(rol_val))
                self.view.tableWidget.setItem(row, 2, QTableWidgetItem(str(u["id_p"])))

            # Apply filter in case text is not empty
            self.filtrar_usuarios()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar usuarios: {str(e)}")

    def filtrar_usuarios(self) -> None:
        filtro = self.view.txtBusquedaCorreo.text().strip().lower()
        for row in range(self.view.tableWidget.rowCount()):
            item = self.view.tableWidget.item(row, 0)
            if item:
                self.view.tableWidget.setRowHidden(row, filtro not in item.text().lower())

    def crear_usuario(self) -> None:
        try:
            role_index = self.view.cmbTipoUsuario.currentIndex()
            role_mapping = {
                0: RolUsuario.ESTUDIANTE,
                1: RolUsuario.COORDINADOR,
                2: RolUsuario.TUTOR_ACADEMICO,
                3: RolUsuario.TUTOR_EMPRESARIAL,
                4: RolUsuario.ADMINISTRADOR,
                5: RolUsuario.EMPRESARIO,
            }
            rol = role_mapping.get(role_index, RolUsuario.ESTUDIANTE)

            patron_correo = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            datos_perfil = {}
            correo = ""

            if role_index == 0:  # Estudiante
                nombre = self.view.txtEstudianteNombre.text().strip()
                cedula = self.view.txtEstudianteCedula.text().strip()
                correo = self.view.txtEstudianteCorreo.text().strip()
                direccion = self.view.txtEstudianteDireccion.text().strip()
                ciclo = self.view.sbxEstudianteCiclo.value()
                matricula_str = self.view.comboBox.currentText()
                estado_matricula = (
                    EstadoMatricula.MATRICULADO if matricula_str == "Matriculado"
                    else EstadoMatricula.NO_MATRICULADO
                )

                if not nombre:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar el nombre.")
                    return
                if not cedula:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar la cédula.")
                    return
                if not correo:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar el correo electrónico.")
                    return
                if not re.match(patron_correo, correo):
                    QMessageBox.critical(
                        self.view, "Error", "El correo electrónico no tiene un formato válido."
                    )
                    return
                if not direccion:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar la dirección.")
                    return

                datos_perfil = {
                    "nombre_y_apellido": nombre,
                    "cedula_dni": cedula,
                    "direccion": direccion,
                    "ciclo_actual": ciclo,
                    "estado_de_matricula": estado_matricula,
                }

            elif role_index in {1, 2, 4}:  # Coordinador, Tutor Academico, Administrador
                nombre = self.view.txtPersonalNombre.text().strip()
                cedula = self.view.txtPersonalCedula.text().strip()
                correo = self.view.txtPersonalCorreo.text().strip()
                direccion = self.view.txtPersonalDireccion.text().strip()

                if not nombre:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar el nombre.")
                    return
                if not cedula:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar la cédula.")
                    return
                if not correo:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar el correo electrónico.")
                    return
                if not re.match(patron_correo, correo):
                    QMessageBox.critical(
                        self.view, "Error", "El correo electrónico no tiene un formato válido."
                    )
                    return
                if not direccion:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar la dirección.")
                    return

                datos_perfil = {
                    "nombre_y_apellido": nombre,
                    "cedula_dni": cedula,
                    "direccion": direccion,
                }

            elif role_index == 3:  # Tutor Empresarial
                nombre = self.view.txtTutorEmpNombre.text().strip()
                cedula = self.view.txtTutorEmpCedula.text().strip()
                correo = self.view.txtTutorEmpCorreo.text().strip()
                direccion = self.view.txtTutorEmpDireccion.text().strip()

                id_e = None
                if self.view.cmbTutorEmpEmpresa.count() > 0:
                    id_e = self.view.cmbTutorEmpEmpresa.currentData()

                if not nombre:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar el nombre.")
                    return
                if not cedula:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar la cédula.")
                    return
                if not correo:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar el correo electrónico.")
                    return
                if not re.match(patron_correo, correo):
                    QMessageBox.critical(
                        self.view, "Error", "El correo electrónico no tiene un formato válido."
                    )
                    return
                if not direccion:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar la dirección.")
                    return
                if id_e is None:
                    QMessageBox.critical(self.view, "Error", "Debe seleccionar una empresa.")
                    return

                datos_perfil = {
                    "nombre_y_apellido": nombre,
                    "cedula_dni": cedula,
                    "direccion": direccion,
                    "id_e": id_e,
                }

            elif role_index == 5:  # Empresa
                nombre = self.view.txtEmpresaNombre.text().strip()
                correo = self.view.txtEmpresaCorreo.text().strip()
                convenio_str = self.view.comboBox_2.currentText()
                estado_convenio = (
                    EstadoConvenio.VIGENTE if convenio_str == "Vigente"
                    else EstadoConvenio.NO_VIGENTE
                )

                if not nombre:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar el nombre.")
                    return
                if not correo:
                    QMessageBox.critical(self.view, "Error", "Debe ingresar el correo electrónico.")
                    return
                if not re.match(patron_correo, correo):
                    QMessageBox.critical(
                        self.view, "Error", "El correo electrónico no tiene un formato válido."
                    )
                    return

                datos_perfil = {
                    "nombre_empresa": nombre,
                    "estado_de_convenio_emp": estado_convenio,
                }

            profile = self.service.crear_cuenta_usuario_sistema(
                correo, "password", rol, datos_perfil
            )
            if profile is not None:
                QMessageBox.information(
                    self.view, "Registro exitoso", "La información fue guardada correctamente."
                )
                self.limpiar_formularios()
                self.ir_a_auditoria()
            else:
                QMessageBox.critical(
                    self.view, "Error al guardar", "No fue posible guardar la información."
                )
        except Exception:
            QMessageBox.critical(
                self.view, "Error al guardar", "No fue posible guardar la información."
            )

    def limpiar_formularios(self) -> None:
        self.view.txtEstudianteNombre.clear()
        self.view.txtEstudianteCedula.clear()
        self.view.txtEstudianteCorreo.clear()
        self.view.txtEstudianteDireccion.clear()
        self.view.sbxEstudianteCiclo.setValue(1)
        self.view.comboBox.setCurrentIndex(0)

        self.view.txtPersonalNombre.clear()
        self.view.txtPersonalCedula.clear()
        self.view.txtPersonalCorreo.clear()
        self.view.txtPersonalDireccion.clear()

        self.view.txtTutorEmpNombre.clear()
        self.view.txtTutorEmpCedula.clear()
        self.view.txtTutorEmpCorreo.clear()
        self.view.txtTutorEmpDireccion.clear()
        if self.view.cmbTutorEmpEmpresa.count() > 0:
            self.view.cmbTutorEmpEmpresa.setCurrentIndex(0)

        self.view.txtEmpresaNombre.clear()
        self.view.txtEmpresaCorreo.clear()
        self.view.comboBox_2.setCurrentIndex(0)

    def eliminar_usuario(self) -> None:
        try:
            selected_items = self.view.tableWidget.selectedItems()
            if not selected_items:
                QMessageBox.warning(
                    self.view, "Selección requerida", "Debe seleccionar un usuario de la tabla."
                )
                return


            row = selected_items[0].row()
            correo_item = self.view.tableWidget.item(row, 0)
            if not correo_item:
                return
            correo = correo_item.text()

            confirm = QMessageBox.question(
                self.view,
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar permanentemente al usuario: {correo}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                success = self.service.eliminar_usuario_sistema(correo)
                if success:
                    QMessageBox.information(
                        self.view, "Baja exitosa", "El usuario fue eliminado correctamente."
                    )
                    self.cargar_usuarios()
                else:
                    QMessageBox.critical(
                        self.view, "Error", "No fue posible eliminar el usuario."
                    )
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al eliminar usuario: {str(e)}")

    def mostrar_acerca_programa(self) -> None:
        self.mostrar_ayuda_dialog(0)

    def mostrar_acerca_desarrollador(self) -> None:
        self.mostrar_ayuda_dialog(1)

    def mostrar_repositorio_github(self) -> None:
        self.mostrar_ayuda_dialog(2)

    def mostrar_ayuda_dialog(self, index: int) -> None:
        dialog = QDialog(self.view)
        uic.loadUi("src/views/ui/wgt_ayuda_acerca.ui", dialog)
        dialog.stackedWidgetAyuda.setCurrentIndex(index)
        dialog.pushButton.clicked.connect(dialog.accept)

        if index == 2:
            QDesktopServices.openUrl(QUrl("https://github.com/LeonardoByte"))

        dialog.exec()
