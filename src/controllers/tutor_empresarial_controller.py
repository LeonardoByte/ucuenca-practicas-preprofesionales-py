from datetime import date
from typing import Optional

from PyQt6 import uic
from PyQt6.QtCore import QObject, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from src.models.estados import EstadoFirmaFormulario
from src.repositories import ActividadRepository
from src.services.exceptions import EvaluacionTempranaError
from src.services.interfaces.tutor_empresarial_main_service_abc import (
    TutorEmpresarialMainServiceABC,
)


class TutorEmpresarialController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: TutorEmpresarialMainServiceABC, tutor_perfil) -> None:
        super().__init__()
        self.view = view
        self.service = service
        self.tutor_perfil = tutor_perfil

        # Load the dynamic UI
        uic.loadUi("src/views/ui/main_window_tutor_empresarial.ui", self.view)

        # Hook navigation (Sidebar buttons)
        self.view.btnNavPracticantes.clicked.connect(self.ir_a_practicantes)
        self.view.btnNavEmpresa.clicked.connect(self.ir_a_empresa)
        self.view.btnNavCerrarSesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Menubar action connections
        self.view.actVerPracticantes.triggered.connect(self.ir_a_practicantes)
        self.view.actVerEmpresa.triggered.connect(self.ir_a_empresa)
        self.view.actCerrarSesion.triggered.connect(self.solicitar_cerrar_sesion)
        self.view.actSalirSistema.triggered.connect(self.salir_sistema)

        # Menu Help connections
        self.view.actAcercaPrograma.triggered.connect(self.mostrar_acerca_programa)
        self.view.actAcercaDesarrollador.triggered.connect(self.mostrar_acerca_desarrollador)
        self.view.actRepositorioGithub.triggered.connect(self.mostrar_repositorio_github)

        # Menu Bitacora action
        self.view.actProponerActividad.triggered.connect(self.proponer_actividad_menu)

        # Action buttons
        self.view.btnVerBitacora.clicked.connect(self.ver_bitacora)
        self.view.btnEvaluarFormulario3.clicked.connect(self.evaluar_formulario3)
        self.view.btnProponerActividad.clicked.connect(self.proponer_actividad)

        # Reactive text filter
        self.view.txtBusquedaAlumno.textChanged.connect(self.filtrar_practicantes)

        # Initial layouts
        self.view.stackedWidgetCentral.setCurrentIndex(0)

        # Load initial data
        self.cargar_datos_empresa()
        self.cargar_practicas()

    def ir_a_practicantes(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(0)

    def ir_a_empresa(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(2)

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

    def cargar_datos_empresa(self) -> None:
        try:
            empresa = self.service.obtener_datos_empresa_tutor(self.tutor_perfil.id_e)
            if empresa:
                self.view.txtNombreEmpresa.setText(empresa.nombre_empresa)
                self.view.txtCorreoElectronicoEmpresa.setText(empresa.correo_electronico)
                contacto = empresa.numeros_contacto[0] if empresa.numeros_contacto else "N/A"
                self.view.txtContactoPrincipalEmpresa.setText(contacto)
                direccion = empresa.direcciones[0] if empresa.direcciones else "N/A"
                self.view.txtDireccionMatrizEmpresa.setText(direccion)
                estado = (
                    empresa.estado_de_convenio_emp.value
                    if hasattr(empresa.estado_de_convenio_emp, "value")
                    else str(empresa.estado_de_convenio_emp)
                )
                self.view.txtEstadoConvenio.setText(estado)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al obtener datos de empresa: {str(e)}")

    def cargar_practicas(self) -> None:
        try:
            practicas = self.service.obtener_practicas_tutor_emp(self.tutor_perfil.id_p)
            self.view.tblPracticas.setRowCount(0)
            for p in practicas:
                row = self.view.tblPracticas.rowCount()
                self.view.tblPracticas.insertRow(row)

                post = self.service.practica_service.postulacion_repo.buscar_por_id(p.id_pos)
                est = (
                    self.service.practica_service.estudiante_repo.buscar_por_id(post.id_p_estudiante)
                    if post else None
                )

                cedula = est.cedula_dni if est else "N/A"
                correo = est.correo_electronico if est else "N/A"
                nombre = est.nombre_y_apellido if est else "N/A"

                self.view.tblPracticas.setItem(row, 0, QTableWidgetItem(cedula))
                self.view.tblPracticas.setItem(row, 1, QTableWidgetItem(nombre))
                self.view.tblPracticas.setItem(row, 2, QTableWidgetItem(correo))
                self.view.tblPracticas.setItem(row, 3, QTableWidgetItem(p.fecha_inicio))
                self.view.tblPracticas.setItem(row, 4, QTableWidgetItem(p.fecha_fin))

                estado = (
                    p.estado_de_practica.value
                    if hasattr(p.estado_de_practica, "value")
                    else str(p.estado_de_practica)
                )
                self.view.tblPracticas.setItem(row, 5, QTableWidgetItem(estado))
                self.view.tblPracticas.item(row, 0).setData(Qt.ItemDataRole.UserRole, p.id_pr)

            self.filtrar_practicantes()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar practicantes: {str(e)}")

    def filtrar_practicantes(self) -> None:
        filtro = self.view.txtBusquedaAlumno.text().strip().lower()
        for row in range(self.view.tblPracticas.rowCount()):
            item = self.view.tblPracticas.item(row, 0)
            if item:
                id_pr = item.data(Qt.ItemDataRole.UserRole)
                practica = self.service.practica_service.practica_repo.buscar_por_id(id_pr)
                post = (
                    self.service.practica_service.postulacion_repo.buscar_por_id(practica.id_pos)
                    if practica else None
                )
                est = (
                    self.service.practica_service.estudiante_repo.buscar_por_id(post.id_p_estudiante)
                    if post else None
                )
                correo = est.correo_electronico.lower() if est else ""
                cedula = est.cedula_dni.lower() if est else ""
                hide = (filtro not in correo) and (filtro not in cedula)
                self.view.tblPracticas.setRowHidden(row, hide)

    def obtener_practica_seleccionada(self) -> Optional[int]:
        selected = self.view.tblPracticas.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblPracticas.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def ver_bitacora(self) -> None:
        id_pr = self.obtener_practica_seleccionada()
        if not id_pr:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar un estudiante de la tabla."
            )
            return

        self.view.stackedWidgetCentral.setCurrentIndex(1)
        self.cargar_bitacora(id_pr)

    def cargar_bitacora(self, id_pr: int) -> None:
        try:
            self.view.tblBitacora.setRowCount(0)
            repo = ActividadRepository()
            repo._cargar_datos()
            actividades = [act for act in repo._datos if act.id_pr == id_pr]

            for act in actividades:
                row = self.view.tblBitacora.rowCount()
                self.view.tblBitacora.insertRow(row)
                self.view.tblBitacora.setItem(row, 0, QTableWidgetItem(act.descripcion_de_la_tarea))
                estado = (
                    act.estado_de_validacion.value
                    if hasattr(act.estado_de_validacion, "value")
                    else str(act.estado_de_validacion)
                )
                self.view.tblBitacora.setItem(row, 1, QTableWidgetItem(estado))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar la bitácora: {str(e)}")

    def proponer_actividad_menu(self) -> None:
        id_pr = self.obtener_practica_seleccionada()
        if not id_pr:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar un estudiante de la tabla."
            )
            return

        self.view.stackedWidgetCentral.setCurrentIndex(1)
        self.cargar_bitacora(id_pr)
        self.view.txaDescripcionActividad.setFocus()

    def proponer_actividad(self) -> None:
        id_pr = self.obtener_practica_seleccionada()
        if not id_pr:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar un estudiante de la tabla."
            )
            return

        descripcion = self.view.txaDescripcionActividad.text().strip()
        if not descripcion:
            QMessageBox.warning(
                self.view, "Campo requerido", "Debe ingresar una descripción para la actividad."
            )
            return

        try:
            actividad = self.service.proponer_actividad_practica(id_pr, descripcion)
            if actividad:
                QMessageBox.information(
                    self.view, "Actividad Registrada", "La actividad fue guardada correctamente."
                )
                self.view.txaDescripcionActividad.clear()
                self.cargar_bitacora(id_pr)
            else:
                QMessageBox.critical(self.view, "Error", "No se pudo proponer la actividad.")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al proponer la actividad: {str(e)}")

    def evaluar_formulario3(self) -> None:
        id_pr = self.obtener_practica_seleccionada()
        if not id_pr:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar un estudiante de la tabla."
            )
            return

        try:
            fecha_actual = date.today().strftime("%Y-%m-%d")
            success = self.service.registrar_evaluacion_formulario3(
                id_pr, EstadoFirmaFormulario.COMPLETADO, fecha_actual
            )
            if success:
                QMessageBox.information(
                    self.view, "Evaluación Guardada", "La información fue guardada correctamente."
                )
                self.cargar_practicas()
            else:
                QMessageBox.critical(self.view, "Error", "No se pudo registrar la evaluación.")
        except EvaluacionTempranaError as e:
            QMessageBox.warning(self.view, "Evaluación Anticipada", str(e))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al evaluar: {str(e)}")

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
