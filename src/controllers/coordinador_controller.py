import json
from PyQt6 import uic
from PyQt6.QtCore import QObject, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
)

from src.models.estados import EstadoPostulacion
from src.repositories import (
    EmpresaRepository,
    EstudianteRepository,
    TutorAcademicoRepository,
    TutorEmpresarialRepository,
)
from src.services.exceptions import DocumentacionIncompletaError
from src.services.interfaces.coordinador_main_service_abc import CoordinadorMainServiceABC
from src.utils.ayuda_dialog import mostrar_ayuda_dialog


class CoordinadorController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: CoordinadorMainServiceABC, coordinador_perfil) -> None:
        super().__init__()
        self.view = view
        self.service = service
        self.coordinador_perfil = coordinador_perfil

        # Instantiate repositories defensively for helper lookups
        self.empresa_repo = EmpresaRepository()
        self.tutor_acad_repo = TutorAcademicoRepository()
        self.estudiante_repo = EstudianteRepository()
        self.tutor_emp_repo = TutorEmpresarialRepository()

        # Load dynamic UI
        uic.loadUi("src/views/ui/main_window_coordinador.ui", self.view)

        # Apply global QSS style to buttons
        from src.utils.qss_loader import aplicar_qss_global
        aplicar_qss_global(self.view)

        # Hook navigation (Sidebar buttons)
        self.view.btnNavPostulaciones.clicked.connect(self.ir_a_postulaciones)
        self.btnNavOfertas = getattr(self.view, "btnNavOfertas", getattr(self.view, "btnNavOferas", None))
        if self.btnNavOfertas:
            self.btnNavOfertas.clicked.connect(self.ir_a_ofertas)
        self.view.btnNavAsignaciones.clicked.connect(self.ir_a_asignaciones)
        self.view.btnNavSolicitudes.clicked.connect(self.ir_a_solicitudes)
        self.view.btnNavCierre.clicked.connect(self.ir_a_cierre)
        self.view.btnNavCerrarSesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Hook menubar actions
        self.view.actRevisarPostulaciones.triggered.connect(self.ir_a_postulaciones)
        self.view.actGenerarTernas.triggered.connect(self.ir_a_postulaciones)
        if hasattr(self.view, "actRevisarOfertas") and self.view.actRevisarOfertas:
            self.view.actRevisarOfertas.triggered.connect(self.ir_a_ofertas)
        self.view.actAsignarTutores.triggered.connect(self.ir_a_asignaciones)
        self.view.actAutorizacionesPendientes.triggered.connect(self.ir_a_solicitudes)
        self.view.actEmitirOficios.triggered.connect(self.ir_a_solicitudes)
        self.view.actCierreOficial.triggered.connect(self.ir_a_cierre)
        self.view.actCerrarSesion.triggered.connect(self.solicitar_cerrar_sesion)
        self.view.actSalirSistema.triggered.connect(self.salir_sistema)

        # Help actions
        self.view.actAcercaPrograma.triggered.connect(self.mostrar_acerca_programa)
        self.view.actAcercaDesarrollador.triggered.connect(self.mostrar_acerca_desarrollador)
        self.view.actRepositorioGithub.triggered.connect(self.mostrar_repositorio_github)

        # Hook page 1 buttons
        self.view.btnValidarPostulacion.clicked.connect(self.validar_postulacion)
        self.view.btnRechazarPostulacion.clicked.connect(self.rechazar_postulacion)
        self.view.btnEnviarTerna.clicked.connect(self.enviar_terna)

        # Hook page 2 buttons (offers tray buttons)
        self.btnAprobarOferta = getattr(self.view, "btnAprobarOferta", getattr(self.view, "btnAceptarOferta", None))
        if self.btnAprobarOferta:
            self.btnAprobarOferta.clicked.connect(self.aprobar_oferta)
        if hasattr(self.view, "btnRechazarOferta") and self.view.btnRechazarOferta:
            self.view.btnRechazarOferta.clicked.connect(self.rechazar_oferta)

        # Hook page 3 buttons
        self.view.btnAsignarTutor.clicked.connect(self.asignar_tutor)

        # Hook page 4 buttons
        self.view.btnAprobarAutorizacion.clicked.connect(self.aprobar_autorizacion)
        self.view.btnRechazarAutorizacion.clicked.connect(self.rechazar_autorizacion)
        self.btnProcesarOficio = getattr(
            self.view, "btnProcesarOficio", getattr(self.view, "pushButton", None)
        )
        if self.btnProcesarOficio:
            self.btnProcesarOficio.clicked.connect(self.procesar_oficio)

        # Hook page 5 buttons
        self.view.btnEjecutarCierre.clicked.connect(self.ejecutar_cierre)

        # Apply controls globally to all tables
        self.tablas = [
            self.view.tblPostulacionesPendientes,
            self.view.tblOfertasConteo,
            getattr(self.view, "tblOfertas", None),
            self.view.tblPracticasSinTutor,
            self.view.tblAutorizacionesPendientes,
            self.view.tblOficiosPendientes,
            self.view.tblPracticasActivas,
        ]
        for tbl in self.tablas:
            if tbl:
                tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
                tbl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Reactive terna button state
        self.view.tblOfertasConteo.itemSelectionChanged.connect(self.actualizar_estado_boton_terna)

        # Set initial layout index
        self.view.stackedWidgetCentral.setCurrentIndex(0)

        # Initial data loading
        self.cargar_postulaciones_y_ofertas()
        self.cargar_tutores_disponibles()
        self.cargar_practicas_sin_tutor()
        self.cargar_solicitudes()
        self.cargar_practicas_activas()
        self.cargar_ofertas_pendientes()

    def ir_a_postulaciones(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(0)
        self.cargar_postulaciones_y_ofertas()

    def ir_a_ofertas(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(1)
        self.cargar_ofertas_pendientes()

    def ir_a_asignaciones(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(2)
        self.cargar_practicas_sin_tutor()
        self.cargar_tutores_disponibles()

    def ir_a_solicitudes(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(3)
        self.cargar_solicitudes()

    def ir_a_cierre(self) -> None:
        self.view.stackedWidgetCentral.setCurrentIndex(4)
        self.cargar_practicas_activas()

    def cargar_ofertas_pendientes(self) -> None:
        try:
            tbl = getattr(self.view, "tblOfertas", None)
            if not tbl:
                return
            tbl.setRowCount(0)
            self.service.oferta_repo._cargar_datos()
            ofertas = self.service.oferta_repo.obtener_todos()
            
            pendientes = [o for o in ofertas if not getattr(o, "validada_por_coordinador", False)]
            
            for o in pendientes:
                row = tbl.rowCount()
                tbl.insertRow(row)
                
                emp = self.empresa_repo.buscar_por_id(o.id_e)
                empresa_nombre = emp.nombre_empresa if emp else "N/A"
                
                try:
                    data = json.loads(o.descripcion_oferta)
                    titulo = data.get("titulo", "")
                except Exception:
                    titulo = o.descripcion_oferta
                
                item_id = QTableWidgetItem(str(o.id_o))
                item_id.setData(Qt.ItemDataRole.UserRole, o.id_o)
                
                tbl.setItem(row, 0, item_id)
                tbl.setItem(row, 1, QTableWidgetItem(titulo))
                tbl.setItem(row, 2, QTableWidgetItem(empresa_nombre))
                tbl.setItem(row, 3, QTableWidgetItem("Pendiente"))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar ofertas pendientes: {str(e)}")

    def aprobar_oferta(self) -> None:
        tbl = getattr(self.view, "tblOfertas", None)
        if not tbl:
            return
        selected = tbl.selectedItems()
        if not selected:
            QMessageBox.warning(self.view, "Selección requerida", "Debe seleccionar una oferta.")
            return
        
        row = selected[0].row()
        item_id = tbl.item(row, 0)
        if not item_id:
            return
        id_o = item_id.data(Qt.ItemDataRole.UserRole)
        
        confirm = QMessageBox.question(
            self.view,
            "Confirmar Aprobación",
            "¿Está seguro que desea aprobar esta oferta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.oferta_repo._cargar_datos()
                oferta = self.service.oferta_repo.buscar_por_id(id_o)
                if oferta:
                    oferta.validada_por_coordinador = True
                    self.service.oferta_repo.guardar(oferta)
                    QMessageBox.information(self.view, "Éxito", "La oferta ha sido aprobada.")
                    self.cargar_ofertas_pendientes()
                else:
                    QMessageBox.critical(self.view, "Error", "No se encontró la oferta.")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al aprobar: {str(e)}")

    def rechazar_oferta(self) -> None:
        tbl = getattr(self.view, "tblOfertas", None)
        if not tbl:
            return
        selected = tbl.selectedItems()
        if not selected:
            QMessageBox.warning(self.view, "Selección requerida", "Debe seleccionar una oferta.")
            return
        
        row = selected[0].row()
        item_id = tbl.item(row, 0)
        if not item_id:
            return
        id_o = item_id.data(Qt.ItemDataRole.UserRole)
        
        confirm = QMessageBox.question(
            self.view,
            "Confirmar Rechazo",
            "¿Está seguro que desea rechazar esta oferta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.oferta_repo._cargar_datos()
                success = self.service.oferta_repo.eliminar(id_o)
                if success:
                    QMessageBox.information(self.view, "Éxito", "La oferta ha sido rechazada.")
                    self.cargar_ofertas_pendientes()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo rechazar la oferta.")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al rechazar: {str(e)}")

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

    # ==========================================
    # Página 1: Postulaciones y Ternas
    # ==========================================
    def cargar_postulaciones_y_ofertas(self) -> None:
        try:
            self.view.tblPostulacionesPendientes.setRowCount(0)
            postulaciones = self.service.revisar_postulaciones_pendientes()

            for p in postulaciones:
                row = self.view.tblPostulacionesPendientes.rowCount()
                self.view.tblPostulacionesPendientes.insertRow(row)

                est = self.estudiante_repo.buscar_por_id(p.id_p_estudiante)
                emp = self.empresa_repo.buscar_por_id(p.id_e)
                oferta = self.service.oferta_repo.buscar_por_id(p.id_o)

                correo = est.correo_electronico if est else "N/A"
                estudiante = est.nombre_y_apellido if est else "N/A"
                empresa = emp.nombre_empresa if emp else "N/A"

                # Unpack description
                try:
                    data = json.loads(oferta.descripcion_oferta)
                    titulo = data.get("titulo", "")
                except Exception:
                    titulo = oferta.descripcion_oferta if oferta else "N/A"

                item_correo = QTableWidgetItem(correo)
                item_correo.setData(Qt.ItemDataRole.UserRole, p.id_pos)

                self.view.tblPostulacionesPendientes.setItem(row, 0, item_correo)
                self.view.tblPostulacionesPendientes.setItem(row, 1, QTableWidgetItem(estudiante))
                self.view.tblPostulacionesPendientes.setItem(row, 2, QTableWidgetItem(empresa))
                self.view.tblPostulacionesPendientes.setItem(row, 3, QTableWidgetItem(titulo))
                self.view.tblPostulacionesPendientes.setItem(
                    row, 4, QTableWidgetItem(p.fecha_postulacion)
                )

            # Ofertas Conteo
            self.view.tblOfertasConteo.setRowCount(0)
            ofertas = self.service.listar_ofertas_con_conteo_validadas()
            for o in ofertas:
                row = self.view.tblOfertasConteo.rowCount()
                self.view.tblOfertasConteo.insertRow(row)

                emp = self.empresa_repo.buscar_por_id(o["id_e"])
                empresa_nombre = emp.nombre_empresa if emp else "N/A"

                try:
                    data = json.loads(o["descripcion_oferta"])
                    titulo = data.get("titulo", "")
                except Exception:
                    titulo = o["descripcion_oferta"]

                item_id = QTableWidgetItem(str(o["id_o"]))
                item_id.setData(Qt.ItemDataRole.UserRole, o["id_o"])

                self.view.tblOfertasConteo.setItem(row, 0, item_id)
                self.view.tblOfertasConteo.setItem(row, 1, QTableWidgetItem(empresa_nombre))
                self.view.tblOfertasConteo.setItem(row, 2, QTableWidgetItem(titulo))
                self.view.tblOfertasConteo.setItem(
                    row, 3, QTableWidgetItem(str(o["conteo_validadas"]))
                )

            self.view.btnEnviarTerna.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(
                self.view, "Error", f"Error al cargar postulaciones u ofertas: {str(e)}"
            )

    def obtener_postulacion_seleccionada(self) -> Optional[int]:
        selected = self.view.tblPostulacionesPendientes.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblPostulacionesPendientes.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def validar_postulacion(self) -> None:
        self._evaluar_postulacion(True)

    def rechazar_postulacion(self) -> None:
        self._evaluar_postulacion(False)

    def _evaluar_postulacion(self, aprobado: bool) -> None:
        id_pos = self.obtener_postulacion_seleccionada()
        if not id_pos:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar una postulación."
            )
            return

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Acción",
            "¿Está seguro que desea dictaminar esta postulación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = self.service.validar_requisitos_alumno(id_pos, aprobado)
                if success:
                    QMessageBox.information(
                        self.view, "Éxito", "La postulación fue procesada correctamente."
                    )
                    self.cargar_postulaciones_y_ofertas()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo procesar la postulación.")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al dictaminar: {str(e)}")

    def actualizar_estado_boton_terna(self) -> None:
        selected = self.view.tblOfertasConteo.selectedItems()
        if not selected:
            self.view.btnEnviarTerna.setEnabled(False)
            return
        row = selected[0].row()
        item_conteo = self.view.tblOfertasConteo.item(row, 3)
        if item_conteo:
            try:
                conteo = int(item_conteo.text())
                self.view.btnEnviarTerna.setEnabled(conteo >= 1)
            except ValueError:
                self.view.btnEnviarTerna.setEnabled(False)
        else:
            self.view.btnEnviarTerna.setEnabled(False)

    def enviar_terna(self) -> None:
        selected = self.view.tblOfertasConteo.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        item_id = self.view.tblOfertasConteo.item(row, 0)
        if not item_id:
            return
        id_o = item_id.data(Qt.ItemDataRole.UserRole)

        is_mock = type(self.view).__name__ in ("MagicMock", "NonCallableMagicMock", "Mock")
        parent_widget = self.view if (isinstance(self.view, QWidget) or is_mock) else None
        confirm = QMessageBox.question(
            parent_widget,
            "Confirmar Terna",
            "¿Está seguro que desea enviar los candidatos para esta oferta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.postulacion_repo._cargar_datos()
                post_ids = [
                    p.id_pos
                    for p in self.service.postulacion_repo._datos
                    if p.id_o == id_o and p.estado_de_postulacion == EstadoPostulacion.VALIDADA
                ]
                if len(post_ids) == 0:
                    QMessageBox.warning(
                        parent_widget, "Validación", "No existen postulaciones validadas."
                    )
                    return

                success = self.service.enviar_terna_a_empresa(post_ids)
                if success:
                    QMessageBox.information(
                        parent_widget, "Terna Enviada", "Los candidatos han sido enviados a la empresa."
                    )
                    self.cargar_postulaciones_y_ofertas()
                else:
                    QMessageBox.critical(parent_widget, "Error", "No se pudo enviar los candidatos.")
            except Exception as e:
                QMessageBox.critical(parent_widget, "Error", f"Error al generar terna: {str(e)}")

    # ==========================================
    # Página 2: Asignación de Tutores
    # ==========================================
    def cargar_practicas_sin_tutor(self) -> None:
        try:
            self.view.tblPracticasSinTutor.setRowCount(0)
            practicas = self.service.listar_practicas_pendientes_de_tutor(
                self.coordinador_perfil.id_p
            )

            for pr in practicas:
                row = self.view.tblPracticasSinTutor.rowCount()
                self.view.tblPracticasSinTutor.insertRow(row)

                post = self.service.postulacion_repo.buscar_por_id(pr.id_pos)
                est = self.estudiante_repo.buscar_por_id(post.id_p_estudiante) if post else None
                emp = self.empresa_repo.buscar_por_id(post.id_e) if post else None

                correo = est.correo_electronico if est else "N/A"
                estudiante = est.nombre_y_apellido if est else "N/A"
                empresa = emp.nombre_empresa if emp else "N/A"

                item_id = QTableWidgetItem(str(pr.id_pr))
                item_id.setData(Qt.ItemDataRole.UserRole, pr.id_pr)

                self.view.tblPracticasSinTutor.setItem(row, 0, item_id)
                self.view.tblPracticasSinTutor.setItem(row, 1, QTableWidgetItem(correo))
                self.view.tblPracticasSinTutor.setItem(row, 2, QTableWidgetItem(estudiante))
                self.view.tblPracticasSinTutor.setItem(row, 3, QTableWidgetItem(empresa))
                self.view.tblPracticasSinTutor.setItem(row, 4, QTableWidgetItem(pr.fecha_inicio))
        except Exception as e:
            QMessageBox.critical(
                self.view, "Error", f"Error al cargar prácticas sin tutor: {str(e)}"
            )

    def cargar_tutores_disponibles(self) -> None:
        try:
            self.view.cmbTutoresDisponibles.clear()
            tutores = self.tutor_acad_repo.obtener_todos()
            for t in tutores:
                self.view.cmbTutoresDisponibles.addItem(t.nombre_y_apellido, t.id_p)
        except Exception as e:
            QMessageBox.critical(
                self.view, "Error", f"Error al cargar tutores disponibles: {str(e)}"
            )

    def obtener_practica_sin_tutor_seleccionada(self) -> Optional[int]:
        selected = self.view.tblPracticasSinTutor.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblPracticasSinTutor.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def asignar_tutor(self) -> None:
        id_pr = self.obtener_practica_sin_tutor_seleccionada()
        if not id_pr:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar una práctica de la tabla."
            )
            return

        id_tutor = self.view.cmbTutoresDisponibles.currentData()
        if not id_tutor:
            QMessageBox.warning(self.view, "Validación", "Debe seleccionar un tutor académico.")
            return

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Asignación",
            "¿Está seguro que desea asignar este tutor a la práctica?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = self.service.asignar_tutor_a_practica(id_pr, id_tutor)
                if success:
                    QMessageBox.information(
                        self.view, "Éxito", "Tutor académico asignado correctamente."
                    )
                    self.cargar_practicas_sin_tutor()
                    self.cargar_practicas_activas()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo asignar el tutor.")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al asignar tutor: {str(e)}")

    # ==========================================
    # Página 3: Autorizaciones y Oficios
    # ==========================================
    def cargar_solicitudes(self) -> None:
        try:
            self.view.tblAutorizacionesPendientes.setRowCount(0)
            auths = self.service.listar_solicitudes_autorizacion_pendientes()
            for s in auths:
                row = self.view.tblAutorizacionesPendientes.rowCount()
                self.view.tblAutorizacionesPendientes.insertRow(row)

                est = self.estudiante_repo.buscar_por_id(s.id_p_estudiante)
                solicitante = est.nombre_y_apellido if est else "N/A"

                item_sol = QTableWidgetItem(solicitante)
                item_sol.setData(Qt.ItemDataRole.UserRole, s.id_sol_aut)

                self.view.tblAutorizacionesPendientes.setItem(row, 0, item_sol)
                self.view.tblAutorizacionesPendientes.setItem(
                    row, 1, QTableWidgetItem(s.nombre_empresa)
                )
                self.view.tblAutorizacionesPendientes.setItem(
                    row, 2, QTableWidgetItem(s.detalles_empresa)
                )
                self.view.tblAutorizacionesPendientes.setItem(
                    row, 3, QTableWidgetItem(s.fecha_solicitud)
                )

            self.view.tblOficiosPendientes.setRowCount(0)
            oficios = self.service.listar_solicitudes_oficio_pendientes()
            for sof in oficios:
                row = self.view.tblOficiosPendientes.rowCount()
                self.view.tblOficiosPendientes.insertRow(row)

                est = self.estudiante_repo.buscar_por_id(sof.id_p_estudiante)
                estudiante = est.nombre_y_apellido if est else "N/A"

                item_est = QTableWidgetItem(estudiante)
                item_est.setData(Qt.ItemDataRole.UserRole, sof.id_sol_of)

                self.view.tblOficiosPendientes.setItem(row, 0, item_est)
                self.view.tblOficiosPendientes.setItem(
                    row, 1, QTableWidgetItem(sof.nombre_destinatario)
                )
                self.view.tblOficiosPendientes.setItem(
                    row, 2, QTableWidgetItem(sof.nombre_empresa)
                )
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar trámites: {str(e)}")

    def obtener_autorizacion_seleccionada(self) -> Optional[int]:
        selected = self.view.tblAutorizacionesPendientes.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblAutorizacionesPendientes.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def obtener_oficio_seleccionado(self) -> Optional[int]:
        selected = self.view.tblOficiosPendientes.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblOficiosPendientes.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def aprobar_autorizacion(self) -> None:
        self._evaluar_autorizacion(True)

    def rechazar_autorizacion(self) -> None:
        self._evaluar_autorizacion(False)

    def _evaluar_autorizacion(self, aprobado: bool) -> None:
        id_sol_aut = self.obtener_autorizacion_seleccionada()
        if not id_sol_aut:
            QMessageBox.warning(
                self.view, "Selección requerida", "Por favor, seleccione una solicitud."
            )
            return

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Acción",
            "¿Está seguro que desea dictaminar esta solicitud de autorización?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = self.service.evaluar_solicitud_autorizacion(
                    id_sol_aut, aprobado, self.coordinador_perfil.id_p, "Representante", "Director"
                )
                if success:
                    QMessageBox.information(
                        self.view, "Éxito", "La solicitud de autorización ha sido procesada."
                    )
                    self.cargar_solicitudes()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo procesar la solicitud.")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al dictaminar: {str(e)}")

    def procesar_oficio(self) -> None:
        id_sol_of = self.obtener_oficio_seleccionado()
        if not id_sol_of:
            QMessageBox.warning(
                self.view, "Selección requerida", "Debe seleccionar un oficio de la tabla."
            )
            return

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Emisión",
            "¿Está seguro que desea emitir este oficio?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = self.service.procesar_emision_oficio(
                    id_sol_of, self.coordinador_perfil.id_p, "oficio_emitido.pdf"
                )
                if success:
                    QMessageBox.information(self.view, "Éxito", "Oficio emitido y firmado.")
                    self.cargar_solicitudes()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo emitir el oficio.")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al emitir oficio: {str(e)}")

    # ==========================================
    # Página 4: Cierre de Expedientes
    # ==========================================
    def cargar_practicas_activas(self) -> None:
        try:
            self.view.tblPracticasActivas.setRowCount(0)
            self.service.practica_repo._cargar_datos()

            # Filter for active/execution practices
            from src.models import EstadoPractica
            practicas = [
                pr
                for pr in self.service.practica_repo._datos
                if pr.estado_de_practica in {EstadoPractica.INICIADA, EstadoPractica.EN_EVALUACION}
            ]

            for pr in practicas:
                row = self.view.tblPracticasActivas.rowCount()
                self.view.tblPracticasActivas.insertRow(row)

                post = self.service.postulacion_repo.buscar_por_id(pr.id_pos)
                est = self.estudiante_repo.buscar_por_id(post.id_p_estudiante) if post else None
                t_acad = self.tutor_acad_repo.buscar_por_id(pr.id_p_tutor_acad) if pr.id_p_tutor_acad != 0 else None
                t_emp = self.tutor_emp_repo.buscar_por_id(pr.id_p_tutor_emp) if pr.id_p_tutor_emp != 0 else None

                estudiante = est.nombre_y_apellido if est else "N/A"
                tutor_acad = t_acad.nombre_y_apellido if t_acad else "Sin asignar"
                tutor_emp = t_emp.nombre_y_apellido if t_emp else "Sin asignar"

                item_est = QTableWidgetItem(estudiante)
                item_est.setData(Qt.ItemDataRole.UserRole, pr.id_pr)

                self.view.tblPracticasActivas.setItem(row, 0, item_est)
                self.view.tblPracticasActivas.setItem(row, 1, QTableWidgetItem(tutor_acad))
                self.view.tblPracticasActivas.setItem(row, 2, QTableWidgetItem(tutor_emp))
                self.view.tblPracticasActivas.setItem(row, 3, QTableWidgetItem(pr.fecha_inicio))
                self.view.tblPracticasActivas.setItem(row, 4, QTableWidgetItem(pr.fecha_fin))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar prácticas activas: {str(e)}")

    def obtener_practica_activa_seleccionada(self) -> Optional[int]:
        selected = self.view.tblPracticasActivas.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.view.tblPracticasActivas.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def ejecutar_cierre(self) -> None:
        id_pr = self.obtener_practica_activa_seleccionada()
        if not id_pr:
            QMessageBox.warning(self.view, "Selección requerida", "Por favor, seleccione una práctica.")
            return

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Cierre",
            "¿Está seguro que desea ejecutar el cierre oficial de esta práctica?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = self.service.ejecutar_cierre_oficial_practica(id_pr)
                if success:
                    QMessageBox.information(
                        self.view,
                        "Cierre oficial exitoso",
                        "El expediente de práctica ha sido cerrado y aprobado oficialmente."
                    )
                    self.cargar_practicas_activas()
                else:
                    QMessageBox.critical(
                        self.view, "Error", "No se pudo realizar el cierre oficial."
                    )
            except DocumentacionIncompletaError as e:
                QMessageBox.critical(self.view, "Error de Documentación", str(e))
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al procesar cierre: {str(e)}")

    # ==========================================
    # Diálogos de Ayuda
    # ==========================================
    def mostrar_acerca_programa(self) -> None:
        mostrar_ayuda_dialog(self.view, 0)

    def mostrar_acerca_desarrollador(self) -> None:
        mostrar_ayuda_dialog(self.view, 1)

    def mostrar_repositorio_github(self) -> None:
        mostrar_ayuda_dialog(self.view, 2)
