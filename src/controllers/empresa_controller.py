import json
from datetime import date
from typing import Optional

from PyQt6 import uic
from PyQt6.QtCore import QObject, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models.estados import EstadoPostulacion
from src.services.interfaces.empresa_main_service_abc import EmpresaMainServiceABC


class EmpresaController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: EmpresaMainServiceABC, empresa_perfil) -> None:
        super().__init__()
        self.view = view
        self.service = service
        self.empresa_perfil = empresa_perfil

        # Load the dynamic UI
        uic.loadUi("src/views/ui/main_window_empresa.ui", self.view)

        # Resolve sidebar buttons
        self.btnNavPublicar = getattr(self.view, "btnNavPublicar", None)
        self.btnNavHistorial = getattr(self.view, "btnNavHistorial", None)
        self.btnNavTutores = getattr(self.view, "btnNavTutores", None)
        self.btnNavCerrarSesion = getattr(self.view, "btnNavCerrarSesion", None)

        if self.btnNavPublicar:
            self.btnNavPublicar.clicked.connect(self.ir_a_publicar)
        if self.btnNavHistorial:
            self.btnNavHistorial.clicked.connect(self.ir_a_historial)
        if self.btnNavTutores:
            self.btnNavTutores.clicked.connect(self.ir_a_tutores)
        if self.btnNavCerrarSesion:
            self.btnNavCerrarSesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Resolve menubar actions
        self.actPublicarOferta = getattr(self.view, "actPublicarOferta", None)
        self.actVerHistorial = getattr(self.view, "actVerHistorial", None)
        self.actVerTutores = getattr(self.view, "actVerTutores", None)
        self.actCerrarSesion = getattr(self.view, "actCerrarSesion", None)
        self.actSalirSistema = getattr(self.view, "actSalirSistema", None)

        if self.actPublicarOferta:
            self.actPublicarOferta.triggered.connect(self.ir_a_publicar)
        if self.actVerHistorial:
            self.actVerHistorial.triggered.connect(self.ir_a_historial)
        if self.actVerTutores:
            self.actVerTutores.triggered.connect(self.ir_a_tutores)
        if self.actCerrarSesion:
            self.actCerrarSesion.triggered.connect(self.solicitar_cerrar_sesion)
        if self.actSalirSistema:
            self.actSalirSistema.triggered.connect(self.salir_sistema)

        # Help actions
        self.view.actAcercaPrograma.triggered.connect(self.mostrar_acerca_programa)
        self.view.actAcercaDesarrollador.triggered.connect(self.mostrar_acerca_desarrollador)
        self.view.actRepositorioGithub.triggered.connect(self.mostrar_repositorio_github)

        # Resolve other action buttons
        self.view.btnPublicar.clicked.connect(self.publicar_oferta)
        self.view.btnVerTerna.clicked.connect(self.ir_a_terna)
        self.view.btnVolverHistorial.clicked.connect(self.ir_a_historial)
        self.view.btnAceptarPostulacion.clicked.connect(self.aceptar_postulacion)
        self.view.btnRechazarPostulacion.clicked.connect(self.rechazar_postulacion)

        # Dar de baja button with fallback
        self.btnDarDeBaja = getattr(
            self.view, "btnDarDeBaja", getattr(self.view, "pushButton", None)
        )
        if self.btnDarDeBaja:
            self.btnDarDeBaja.clicked.connect(self.dar_de_baja)

        # Reactive filters
        self.view.txtFiltradoOferta.textChanged.connect(self.filtrar_ofertas)
        self.view.txtBusquedaTutor.textChanged.connect(self.filtrar_tutores)

        # Initial layouts
        self.view.stackedWidgetCentral.setCurrentIndex(0)

        # Load initial data
        self.cargar_ofertas()
        self.cargar_tutores()

    def ir_a_publicar(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(0)

    def ir_a_historial(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(1)
        self.cargar_ofertas()

    def ir_a_tutores(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(3)
        self.cargar_tutores()

    def ir_a_terna(self) -> None:
        id_o = self.obtener_oferta_seleccionada()
        if not id_o:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar una oferta de la tabla."
            )
            return

        self.view.stackedWidgetCentral.setCurrentIndex(2)
        self.cargar_terna(id_o)

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

    def publicar_oferta(self) -> None:
        titulo = self.view.txtTituloOferta.text().strip()
        desc = self.view.txtDescripcionOferta.text().strip()
        requisitos = self.view.txaRequisitos.text().strip()
        duracion = self.view.txtDuracionOferta.text().strip()
        remuneracion = self.view.dspnRemuneracion.value()

        if not titulo or not requisitos:
            QMessageBox.warning(self.view, "Validación", "Debe ingresar el nombre.")
            return

        # Pack title and description into a JSON string stored in description
        package = {"titulo": titulo, "descripcion": desc}
        descripcion_json = json.dumps(package)

        fecha_pub = date.today().strftime("%Y-%m-%d")

        try:
            oferta = self.service.registrar_oferta(
                self.empresa_perfil.id_e,
                descripcion_json,
                requisitos,
                fecha_pub,
                duracion,
                remuneracion,
            )
            if oferta is not None:
                QMessageBox.information(
                    self.view, "Éxito", "La oferta fue publicada correctamente."
                )
                self.view.txtTituloOferta.clear()
                self.view.txtDescripcionOferta.clear()
                self.view.txaRequisitos.clear()
                self.view.txtDuracionOferta.clear()
                self.view.dspnRemuneracion.setValue(0.0)
                self.cargar_ofertas()
            else:
                QMessageBox.critical(self.view, "Error", "No se pudo registrar la oferta.")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al publicar oferta: {str(e)}")

    def cargar_ofertas(self) -> None:
        try:
            self.view.tblOfertasHistorico.setRowCount(0)
            ofertas = self.service.listar_mis_ofertas_publicadas(self.empresa_perfil.id_e)

            for o in ofertas:
                row = self.view.tblOfertasHistorico.rowCount()
                self.view.tblOfertasHistorico.insertRow(row)

                # Unpack title and description
                try:
                    data = json.loads(o.descripcion_oferta)
                    titulo = data.get("titulo", "")
                    descripcion = data.get("descripcion", "")
                except (json.JSONDecodeError, TypeError, AttributeError, ValueError):
                    titulo = o.descripcion_oferta
                    descripcion = ""

                item_titulo = QTableWidgetItem(titulo)
                item_titulo.setData(Qt.ItemDataRole.UserRole, o.id_o)

                self.view.tblOfertasHistorico.setItem(row, 0, item_titulo)
                self.view.tblOfertasHistorico.setItem(row, 1, QTableWidgetItem(descripcion))
                self.view.tblOfertasHistorico.setItem(row, 2, QTableWidgetItem(o.requisitos))
                self.view.tblOfertasHistorico.setItem(
                    row, 3, QTableWidgetItem(o.fecha_de_publicacion)
                )

            self.filtrar_ofertas()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar ofertas: {str(e)}")

    def filtrar_ofertas(self) -> None:
        filtro = self.view.txtFiltradoOferta.text().strip().lower()
        for row in range(self.view.tblOfertasHistorico.rowCount()):
            item = self.view.tblOfertasHistorico.item(row, 0)
            if item:
                titulo = item.text().lower()
                hide = filtro not in titulo
                self.view.tblOfertasHistorico.setRowHidden(row, hide)

    def obtener_oferta_seleccionada(self) -> Optional[int]:
        selected = self.view.tblOfertasHistorico.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblOfertasHistorico.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def dar_de_baja(self) -> None:
        id_o = self.obtener_oferta_seleccionada()
        if not id_o:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar una oferta de la tabla."
            )
            return

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Baja",
            "¿Está seguro que desea dar de baja esta oferta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = self.service.oferta_service.repo.eliminar(id_o)
                if success:
                    QMessageBox.information(
                        self.view, "Baja exitosa", "La oferta ha sido dada de baja."
                    )
                    self.cargar_ofertas()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo dar de baja la oferta.")
            except Exception as e:
                QMessageBox.critical(
                    self.view, "Error", f"Error al dar de baja la oferta: {str(e)}"
                )

    def cargar_terna(self, id_o: int) -> None:
        try:
            self.view.tblPostulantesTerna.setRowCount(0)
            self.view.tblPostulantesTerna.setProperty("current_id_o", id_o)

            self.service.postulacion_service.repo._cargar_datos()
            id_terna = None
            for p in self.service.postulacion_service.repo._datos:
                if p.id_o == id_o and p.id_terna is not None:
                    id_terna = p.id_terna
                    break

            candidatos = []
            if id_terna is not None:
                candidatos = self.service.visualizar_terna_recibida(id_terna)

            for cand in candidatos:
                row = self.view.tblPostulantesTerna.rowCount()
                self.view.tblPostulantesTerna.insertRow(row)

                est = self.service.practica_service.estudiante_repo.buscar_por_id(
                    cand.id_p_estudiante
                )
                cedula = est.cedula_dni if est else "N/A"
                nombre = est.nombre_y_apellido if est else "N/A"
                correo = est.correo_electronico if est else "N/A"

                item_ced = QTableWidgetItem(cedula)
                item_ced.setData(Qt.ItemDataRole.UserRole, cand.id_pos)

                self.view.tblPostulantesTerna.setItem(row, 0, item_ced)
                self.view.tblPostulantesTerna.setItem(row, 1, QTableWidgetItem(nombre))
                self.view.tblPostulantesTerna.setItem(row, 2, QTableWidgetItem(correo))

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar la terna: {str(e)}")

    def obtener_postulacion_seleccionada(self) -> Optional[int]:
        selected = self.view.tblPostulantesTerna.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblPostulantesTerna.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def aceptar_postulacion(self) -> None:
        id_pos = self.obtener_postulacion_seleccionada()
        if not id_pos:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar un postulante."
            )
            return

        # Show dynamic QDialog to specify tutor, start/end dates
        parent = self.view if isinstance(self.view, QWidget) else None
        dialog = QDialog(parent)
        dialog.setWindowTitle("Aceptar Postulación y Formalizar Práctica")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout(dialog)

        # Tutor selection
        layout.addWidget(QLabel("Seleccione el Tutor Empresarial:", dialog))
        combo_tutor = QComboBox(dialog)
        tutores = self.service.obtener_tutores_de_empresa(self.empresa_perfil.id_e)
        for t in tutores:
            combo_tutor.addItem(t.nombre_y_apellido, t.id_p)
        layout.addWidget(combo_tutor)

        # Start date
        layout.addWidget(QLabel("Fecha de Inicio (AAAA-MM-DD):", dialog))
        txt_inicio = QLineEdit(dialog)
        txt_inicio.setText("2026-06-05")
        layout.addWidget(txt_inicio)

        # End date
        layout.addWidget(QLabel("Fecha de Fin (AAAA-MM-DD):", dialog))
        txt_fin = QLineEdit(dialog)
        txt_fin.setText("2026-12-05")
        layout.addWidget(txt_fin)

        # Submit button
        btn_save = QPushButton("Formalizar", dialog)
        btn_save.clicked.connect(dialog.accept)
        layout.addWidget(btn_save)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            id_tutor = combo_tutor.currentData()
            fecha_ini = txt_inicio.text().strip()
            fecha_f = txt_fin.text().strip()

            if not id_tutor or not fecha_ini or not fecha_f:
                QMessageBox.warning(self.view, "Error", "Debe completar todos los datos.")
                return

            try:
                success = self.service.seleccionar_candidato_ganador(
                    id_pos, id_tutor, fecha_ini, fecha_f
                )
                if success:
                    QMessageBox.information(
                        self.view, "Éxito", "La contratación se completó correctamente."
                    )
                    self.view.stackedWidgetCentral.setCurrentIndex(1)
                    self.cargar_ofertas()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo formalizar la práctica.")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error en la formalización: {str(e)}")

    def rechazar_postulacion(self) -> None:
        id_pos = self.obtener_postulacion_seleccionada()
        if not id_pos:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar un postulante."
            )
            return

        try:
            success = self.service.postulacion_service.cambiar_estado(
                id_pos, EstadoPostulacion.RECHAZADA
            )
            if success:
                QMessageBox.information(
                    self.view, "Éxito", "La postulación fue rechazada correctamente."
                )
                id_o = self.view.tblPostulantesTerna.property("current_id_o")
                self.cargar_terna(id_o)
            else:
                QMessageBox.critical(self.view, "Error", "No se pudo rechazar la postulación.")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al rechazar postulación: {str(e)}")

    def cargar_tutores(self) -> None:
        try:
            self.view.tableWidget.setRowCount(0)
            tutores = self.service.obtener_tutores_de_empresa(self.empresa_perfil.id_e)

            for t in tutores:
                row = self.view.tableWidget.rowCount()
                self.view.tableWidget.insertRow(row)

                self.view.tableWidget.setItem(row, 0, QTableWidgetItem(t.cedula_dni))
                self.view.tableWidget.setItem(row, 1, QTableWidgetItem(t.nombre_y_apellido))
                self.view.tableWidget.setItem(row, 2, QTableWidgetItem(t.correo_electronico))

            self.filtrar_tutores()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar tutores: {str(e)}")

    def filtrar_tutores(self) -> None:
        filtro = self.view.txtBusquedaTutor.text().strip().lower()
        for row in range(self.view.tableWidget.rowCount()):
            item_ced = self.view.tableWidget.item(row, 0)
            item_correo = self.view.tableWidget.item(row, 2)

            ced = item_ced.text().lower() if item_ced else ""
            correo = item_correo.text().lower() if item_correo else ""

            hide = (filtro not in ced) and (filtro not in correo)
            self.view.tableWidget.setRowHidden(row, hide)

    def mostrar_acerca_programa(self) -> None:
        self.mostrar_ayuda_dialog(0)

    def mostrar_acerca_desarrollador(self) -> None:
        self.mostrar_ayuda_dialog(1)

    def mostrar_repositorio_github(self) -> None:
        self.mostrar_ayuda_dialog(2)

    def mostrar_ayuda_dialog(self, index: int) -> None:
        parent = self.view if isinstance(self.view, QWidget) else None
        dialog = QDialog(parent)
        uic.loadUi("src/views/ui/wgt_ayuda_acerca.ui", dialog)
        dialog.stackedWidgetAyuda.setCurrentIndex(index)
        dialog.pushButton.clicked.connect(dialog.accept)

        if index == 2:
            QDesktopServices.openUrl(QUrl("https://github.com/LeonardoByte"))

        dialog.exec()
