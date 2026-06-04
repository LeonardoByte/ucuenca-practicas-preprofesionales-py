from datetime import date, datetime
from typing import Optional

from PyQt6 import uic
from PyQt6.QtCore import QObject, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.models.estados import EstadoFirmaFormulario, EstadoValidacionActividad
from src.services.interfaces.tutor_academico_main_service_abc import (
    TutorAcademicoMainServiceABC,
)


class TutorAcademicoController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: TutorAcademicoMainServiceABC, tutor_perfil) -> None:
        super().__init__()
        self.view = view
        self.service = service
        self.tutor_perfil = tutor_perfil

        # Load the dynamic UI
        uic.loadUi("src/views/ui/main_window_tutor_academico.ui", self.view)

        # Resolve sidebar buttons with fallback
        self.btnNavEstudiantes = getattr(
            self.view, "btnNavEstudiantes", getattr(self.view, "pushButton", None)
        )
        self.btnNavBitacora = getattr(
            self.view, "btnNavBitacora", getattr(self.view, "pushButton_2", None)
        )
        self.btnNavCerrarSesion = getattr(
            self.view, "btnNavCerrarSesion", getattr(self.view, "pushButton_3", None)
        )

        # Hook navigation (Sidebar buttons)
        if self.btnNavEstudiantes:
            self.btnNavEstudiantes.clicked.connect(self.ir_a_estudiantes)
        if self.btnNavBitacora:
            self.btnNavBitacora.clicked.connect(self.ir_a_bitacora_menu)
        if self.btnNavCerrarSesion:
            self.btnNavCerrarSesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Menubar actions with fallback
        self.actVerEstudiantes = getattr(self.view, "actVerEstudiantes", None)
        self.actAuditarBitacora = getattr(
            self.view,
            "actAuditarBitacora",
            getattr(self.view, "actAuditoriaUsuarios", None),
        )
        self.actCerrarSesion = getattr(self.view, "actCerrarSesion", None)
        self.actSalirSistema = getattr(self.view, "actSalirSistema", None)

        if self.actVerEstudiantes:
            self.actVerEstudiantes.triggered.connect(self.ir_a_estudiantes)
        if self.actAuditarBitacora:
            self.actAuditarBitacora.triggered.connect(self.ir_a_bitacora_menu)
        if self.actCerrarSesion:
            self.actCerrarSesion.triggered.connect(self.solicitar_cerrar_sesion)
        if self.actSalirSistema:
            self.actSalirSistema.triggered.connect(self.salir_sistema)

        # Menu Help actions
        self.view.actAcercaPrograma.triggered.connect(self.mostrar_acerca_programa)
        self.view.actAcercaDesarrollador.triggered.connect(self.mostrar_acerca_desarrollador)
        self.view.actRepositorioGithub.triggered.connect(self.mostrar_repositorio_github)

        # Action buttons
        self.view.btnAuditarBitacora.clicked.connect(self.ir_a_bitacora)
        self.view.btnEvaluarFormulario2.clicked.connect(self.evaluar_formulario2)
        self.view.btnValidarActividad.clicked.connect(self.validar_actividad)
        self.view.btnRechazarActividad.clicked.connect(self.rechazar_actividad)

        # Reactive text filter
        self.view.txtBusquedaEstudiante.textChanged.connect(self.filtrar_estudiantes)

        # Initial layouts
        self.view.stackedWidgetCentral.setCurrentIndex(0)

        # Load initial data
        self.cargar_practicas()

    def ir_a_estudiantes(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(0)

    def ir_a_bitacora_menu(self) -> None:
        self.ir_a_bitacora()

    def ir_a_bitacora(self) -> None:
        id_pr = self.obtener_practica_seleccionada()
        if not id_pr:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar un estudiante de la tabla."
            )
            return

        self.view.stackedWidgetCentral.setCurrentIndex(1)
        self.cargar_actividades_bitacora(id_pr)

    def cargar_practicas(self) -> None:
        try:
            practicas = self.service.obtener_practicas_tutor_acad(self.tutor_perfil.id_p)
            self.view.tblEstudiantes.setRowCount(0)
            for p in practicas:
                row = self.view.tblEstudiantes.rowCount()
                self.view.tblEstudiantes.insertRow(row)

                post = self.service.practica_service.postulacion_repo.buscar_por_id(p.id_pos)
                est = (
                    self.service.practica_service.estudiante_repo.buscar_por_id(post.id_p_estudiante)
                    if post else None
                )

                cedula = est.cedula_dni if est else "N/A"
                correo = est.correo_electronico if est else "N/A"
                nombre = est.nombre_y_apellido if est else "N/A"

                self.view.tblEstudiantes.setItem(row, 0, QTableWidgetItem(cedula))
                self.view.tblEstudiantes.setItem(row, 1, QTableWidgetItem(correo))
                self.view.tblEstudiantes.setItem(row, 2, QTableWidgetItem(nombre))
                self.view.tblEstudiantes.setItem(row, 3, QTableWidgetItem(p.fecha_inicio))
                self.view.tblEstudiantes.setItem(row, 4, QTableWidgetItem(p.fecha_fin))

                estado = (
                    p.estado_de_practica.value
                    if hasattr(p.estado_de_practica, "value")
                    else str(p.estado_de_practica)
                )
                self.view.tblEstudiantes.setItem(row, 5, QTableWidgetItem(estado))
                self.view.tblEstudiantes.item(row, 0).setData(Qt.ItemDataRole.UserRole, p.id_pr)

            self.view.btnEvaluarFormulario2.setEnabled(True)
            self.filtrar_estudiantes()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar practicantes: {str(e)}")

    def filtrar_estudiantes(self) -> None:
        filtro = self.view.txtBusquedaEstudiante.text().strip().lower()
        for row in range(self.view.tblEstudiantes.rowCount()):
            item = self.view.tblEstudiantes.item(row, 0)
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
                self.view.tblEstudiantes.setRowHidden(row, hide)

    def obtener_practica_seleccionada(self) -> Optional[int]:
        selected = self.view.tblEstudiantes.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblEstudiantes.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def cargar_actividades_bitacora(self, id_pr: int) -> None:
        try:
            self.view.tblBitacoraAuditoria.setRowCount(0)
            actividades = self.service.listar_actividades_de_practica(id_pr)
            for act in actividades:
                row = self.view.tblBitacoraAuditoria.rowCount()
                self.view.tblBitacoraAuditoria.insertRow(row)
                item = QTableWidgetItem(act.descripcion_de_la_tarea)
                item.setData(Qt.ItemDataRole.UserRole, act.id_act)
                self.view.tblBitacoraAuditoria.setItem(row, 0, item)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar la bitácora: {str(e)}")

    def obtener_actividad_seleccionada(self) -> Optional[int]:
        selected = self.view.tblBitacoraAuditoria.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblBitacoraAuditoria.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def validar_actividad(self) -> None:
        self._evaluar_actividad(EstadoValidacionActividad.VALIDADA)

    def rechazar_actividad(self) -> None:
        self._evaluar_actividad(EstadoValidacionActividad.RECHAZADA)

    def _evaluar_actividad(self, estado: EstadoValidacionActividad) -> None:
        id_pr = self.obtener_practica_seleccionada()
        id_act = self.obtener_actividad_seleccionada()
        if not id_pr or not id_act:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar una actividad de la tabla."
            )
            return

        try:
            success = self.service.evaluar_actividad_alumno(id_act, id_pr, estado)
            if success:
                accion = "validada" if estado == EstadoValidacionActividad.VALIDADA else "rechazada"
                QMessageBox.information(
                    self.view, "Actividad Evaluada", f"La actividad fue {accion} correctamente."
                )
                self.cargar_actividades_bitacora(id_pr)
            else:
                QMessageBox.critical(self.view, "Error", "No se pudo evaluar la actividad.")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al evaluar la actividad: {str(e)}")

    def evaluar_formulario2(self) -> None:
        id_pr = self.obtener_practica_seleccionada()
        if not id_pr:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar un estudiante de la tabla."
            )
            return

        try:
            practica = self.service.practica_service.practica_repo.buscar_por_id(id_pr)
            if not practica:
                QMessageBox.critical(self.view, "Error", "No se encontró la práctica.")
                return

            fecha_fin_dt = datetime.strptime(practica.fecha_fin, "%Y-%m-%d").date()
            fecha_actual_dt = date.today()
            diferencia_dias = (fecha_fin_dt - fecha_actual_dt).days
            if diferencia_dias > 7:
                QMessageBox.warning(
                    self.view,
                    "Evaluación Anticipada",
                    "No se puede registrar la evaluación final con más de 7 días "
                    "de anticipación al término de la práctica."
                )
                self.view.btnEvaluarFormulario2.setEnabled(False)
                return

            # Display the signature dropdown
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Firma de Formulario 2")
            layout = QVBoxLayout(dialog)

            label = QLabel("Seleccione el estado de la firma:", dialog)
            layout.addWidget(label)

            combo = QComboBox(dialog)
            for e in EstadoFirmaFormulario:
                combo.addItem(e.value, e)
            layout.addWidget(combo)

            btn_save = QPushButton("Guardar", dialog)
            btn_save.clicked.connect(dialog.accept)
            layout.addWidget(btn_save)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_enum = combo.currentData()
                fecha_actual = date.today().strftime("%Y-%m-%d")
                success = self.service.registrar_evaluacion_formulario2(
                    id_pr, selected_enum, fecha_actual
                )
                if success:
                    QMessageBox.information(
                        self.view,
                        "Evaluación Guardada",
                        "La información fue guardada correctamente."
                    )
                    self.cargar_practicas()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo registrar la evaluación.")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al evaluar: {str(e)}")

    def solicitar_cerrar_sesion(self) -> None:
        confirm = QMessageBox.question(
            self.view,
            "Confirmar Cierre de Sesión",
            "¿Está seguro de cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.cerrar_sesion.emit()

    def salir_sistema(self) -> None:
        confirm = QMessageBox.question(
            self.view,
            "Salir del Sistema",
            "¿Está seguro que desea salir del sistema?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.view.close()

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
