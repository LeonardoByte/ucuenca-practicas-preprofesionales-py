import json
from datetime import date

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

from src.repositories import (
    ActividadRepository,
    EmpresaRepository,
    OfertaRepository,
    PostulacionRepository,
)
from src.services.exceptions import (
    CicloNoPermitidoError,
    EstudianteConPracticaActivaError,
    RequisitosNoCumplidosError,
)
from src.services.interfaces.estudiante_main_service_abc import EstudianteMainServiceABC


class EstudianteController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: EstudianteMainServiceABC, estudiante_perfil) -> None:
        super().__init__()
        self.view = view
        self.service = service
        self.estudiante_perfil = estudiante_perfil

        # Repositories for view loading and mock data searches
        self.empresa_repo = EmpresaRepository()
        self.oferta_repo = OfertaRepository()
        self.postulacion_repo = PostulacionRepository()
        self.actividad_repo = ActividadRepository()

        # Load dynamic UI only if base instance is a QWidget
        if isinstance(self.view, QWidget):
            uic.loadUi("src/views/ui/main_window_estudiante.ui", self.view)

        # Hook navigation (Sidebar buttons)
        if hasattr(self.view, "btnNavOfertas") and self.view.btnNavOfertas:
            self.view.btnNavOfertas.clicked.connect(self.ir_a_ofertas)
        if hasattr(self.view, "btnNavPostulaciones") and self.view.btnNavPostulaciones:
            self.view.btnNavPostulaciones.clicked.connect(self.ir_a_postulaciones)
        if hasattr(self.view, "btnNavSolicitar") and self.view.btnNavSolicitar:
            self.view.btnNavSolicitar.clicked.connect(self.ir_a_solicitudes)
        if hasattr(self.view, "btnNavBitacora") and self.view.btnNavBitacora:
            self.view.btnNavBitacora.clicked.connect(self.ir_a_bitacora)
        if hasattr(self.view, "btnNavCerrarSesion") and self.view.btnNavCerrarSesion:
            self.view.btnNavCerrarSesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Hook menubar actions
        if hasattr(self.view, "actVerOfertas") and self.view.actVerOfertas:
            self.view.actVerOfertas.triggered.connect(self.ir_a_ofertas)
        if hasattr(self.view, "actMisPostulaciones") and self.view.actMisPostulaciones:
            self.view.actMisPostulaciones.triggered.connect(self.ir_a_postulaciones)
        if hasattr(self.view, "actSolicitarAutorizacion") and self.view.actSolicitarAutorizacion:
            self.view.actSolicitarAutorizacion.triggered.connect(self.ir_a_solicitudes)
        if hasattr(self.view, "actVerActividades") and self.view.actVerActividades:
            self.view.actVerActividades.triggered.connect(self.ir_a_bitacora)
        if hasattr(self.view, "actRegistrarActividad") and self.view.actRegistrarActividad:
            self.view.actRegistrarActividad.triggered.connect(self.ir_a_bitacora)
        if hasattr(self.view, "actCerrarSesion") and self.view.actCerrarSesion:
            self.view.actCerrarSesion.triggered.connect(self.solicitar_cerrar_sesion)
        if hasattr(self.view, "actSalirSistema") and self.view.actSalirSistema:
            self.view.actSalirSistema.triggered.connect(self.salir_sistema)

        # Hook help actions
        if hasattr(self.view, "actAcercaPrograma") and self.view.actAcercaPrograma:
            self.view.actAcercaPrograma.triggered.connect(self.mostrar_acerca_programa)
        if hasattr(self.view, "actAcercaDesarrollador") and self.view.actAcercaDesarrollador:
            self.view.actAcercaDesarrollador.triggered.connect(self.mostrar_acerca_desarrollador)
        if hasattr(self.view, "actRepositorioGithub") and self.view.actRepositorioGithub:
            self.view.actRepositorioGithub.triggered.connect(self.mostrar_repositorio_github)

        # Hook Page 1 button
        if hasattr(self.view, "btnPostularOferta") and self.view.btnPostularOferta:
            self.view.btnPostularOferta.clicked.connect(self.postular_oferta)

        # Hook Page 3 button
        if hasattr(self.view, "btnEnviarSolicitud") and self.view.btnEnviarSolicitud:
            self.view.btnEnviarSolicitud.clicked.connect(self.enviar_solicitud)

        # Hook Page 4 button (resolved dynamically to handle spec naming difference)
        self.btnGuardarActividad = getattr(
            self.view, "btnGuardarActividad", getattr(self.view, "btnProponerActividad", None)
        )
        if self.btnGuardarActividad:
            self.btnGuardarActividad.clicked.connect(self.guardar_actividad)

        # Hook legacy actions/buttons to maintain compatibility with legacy tests
        if hasattr(self.view, "btn_nav_catalogo") and self.view.btn_nav_catalogo:
            self.view.btn_nav_catalogo.clicked.connect(self.ir_a_ofertas)
        if hasattr(self.view, "btn_nav_postulaciones") and self.view.btn_nav_postulaciones:
            self.view.btn_nav_postulaciones.clicked.connect(self.ir_a_postulaciones)
        if hasattr(self.view, "btn_nav_tramites") and self.view.btn_nav_tramites:
            self.view.btn_nav_tramites.clicked.connect(self.ir_a_solicitudes)
        if hasattr(self.view, "btn_nav_bitacora") and self.view.btn_nav_bitacora:
            self.view.btn_nav_bitacora.clicked.connect(self.ir_a_bitacora)
        if hasattr(self.view, "btn_cerrar_sesion") and self.view.btn_cerrar_sesion:
            self.view.btn_cerrar_sesion.clicked.connect(self.solicitar_cerrar_sesion)
        if hasattr(self.view, "btn_aplicar_vacante") and self.view.btn_aplicar_vacante:
            self.view.btn_aplicar_vacante.clicked.connect(self.aplicar_a_vacante)
        if (
            hasattr(self.view, "btn_enviar_sol_autorizacion")
            and self.view.btn_enviar_sol_autorizacion
        ):
            self.view.btn_enviar_sol_autorizacion.clicked.connect(self.solicitar_autorizacion)
        if hasattr(self.view, "btn_enviar_sol_oficio") and self.view.btn_enviar_sol_oficio:
            self.view.btn_enviar_sol_oficio.clicked.connect(self.solicitar_oficio)
        if hasattr(self.view, "btn_registrar_actividad") and self.view.btn_registrar_actividad:
            self.view.btn_registrar_actividad.clicked.connect(self.registrar_actividad_bitacora)

        # Apply controls globally to all tables
        self.tablas = [
            getattr(self.view, "tblOfertasDisponibles", None),
            getattr(self.view, "tblMisPostulaciones", None),
            getattr(self.view, "tblMisActividades", None),
        ]
        for tbl in self.tablas:
            if tbl:
                tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
                tbl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Connect text filter on catalog page
        if hasattr(self.view, "txtFiltradoOfertas") and self.view.txtFiltradoOfertas:
            self.view.txtFiltradoOfertas.textChanged.connect(self.filtrar_ofertas)

        # Initial load: detect legacy mock interface versus actual UI
        if hasattr(self.view, "mostrar_catalogo_ofertas"):
            self.cargar_catalogo()
            if hasattr(self.view, "mostrar_mis_postulaciones"):
                self.cargar_mis_postulaciones_legacy()
            if hasattr(self.view, "mostrar_mis_solicitudes_autorizacion"):
                self.cargar_tramites_legacy()
        else:
            self.ir_a_ofertas()

    # ==========================================
    # Navigation
    # ==========================================
    def ir_a_ofertas(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("catalogo")
        if hasattr(self.view, "stackedWidgetCentral") and self.view.stackedWidgetCentral:
            self.view.stackedWidgetCentral.setCurrentIndex(0)
        self.cargar_ofertas()

    def ir_a_postulaciones(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("postulaciones")
        if hasattr(self.view, "stackedWidgetCentral") and self.view.stackedWidgetCentral:
            self.view.stackedWidgetCentral.setCurrentIndex(1)
        self.cargar_mis_postulaciones()

    def ir_a_solicitudes(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("tramites")
        if hasattr(self.view, "stackedWidgetCentral") and self.view.stackedWidgetCentral:
            self.view.stackedWidgetCentral.setCurrentIndex(2)

    def ir_a_bitacora(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("bitacora")

        if hasattr(self.view, "bloquear_bitacora") or hasattr(self.view, "mostrar_advertencia"):
            self.validar_y_cargar_bitacora()
        else:
            if hasattr(self.view, "stackedWidgetCentral") and self.view.stackedWidgetCentral:
                self.view.stackedWidgetCentral.setCurrentIndex(3)
            self.cargar_mis_actividades()

    def solicitar_cerrar_sesion(self) -> None:
        if hasattr(self.view, "confirmar_accion"):
            if not self.view.confirmar_accion("¿Está seguro de cerrar sesión?"):
                return
            self.cerrar_sesion.emit()
            return

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Cierre de Sesión",
            "¿Está seguro de cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.view.close()
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
    # Page 1: Catálogo de Ofertas
    # ==========================================
    def cargar_ofertas(self) -> None:
        tbl = getattr(self.view, "tblOfertasDisponibles", None)
        if not tbl:
            return
        try:
            tbl.setRowCount(0)
            ofertas = self.service.obtener_catalogo_ofertas(self.estudiante_perfil.id_p)
            for o in ofertas:
                row = tbl.rowCount()
                tbl.insertRow(row)

                # Fetch company details
                emp = self.empresa_repo.buscar_por_id(o.id_e)
                empresa_nombre = emp.nombre_empresa if emp else "N/A"

                # Deserialise description if JSON format
                try:
                    data = json.loads(o.descripcion_oferta)
                    titulo = data.get("titulo", "")
                except Exception:
                    titulo = o.descripcion_oferta

                item_titulo = QTableWidgetItem(titulo)
                # Store offer ID and company ID in user role data
                item_titulo.setData(Qt.ItemDataRole.UserRole, (o.id_o, o.id_e))

                tbl.setItem(row, 0, item_titulo)
                tbl.setItem(row, 1, QTableWidgetItem(empresa_nombre))
                tbl.setItem(row, 2, QTableWidgetItem(o.duracion))
                tbl.setItem(row, 3, QTableWidgetItem(f"${o.remuneracion:.2f}"))
                tbl.setItem(row, 4, QTableWidgetItem(o.requisitos))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar ofertas: {str(e)}")

    def filtrar_ofertas(self) -> None:
        tbl = getattr(self.view, "tblOfertasDisponibles", None)
        txt = getattr(self.view, "txtFiltradoOfertas", None)
        if not tbl or not txt:
            return
        search_text = txt.text().strip().lower()
        for row in range(tbl.rowCount()):
            item = tbl.item(row, 0)
            if item:
                titulo = item.text().lower()
                tbl.setRowHidden(row, search_text not in titulo)

    def postular_oferta(self) -> None:
        tbl = getattr(self.view, "tblOfertasDisponibles", None)
        if not tbl:
            return
        selected = tbl.selectedItems()
        if not selected:
            QMessageBox.warning(self.view, "Selección requerida", "Debe seleccionar una oferta.")
            return

        row = selected[0].row()
        item_titulo = tbl.item(row, 0)
        if not item_titulo:
            return

        id_o, id_e = item_titulo.data(Qt.ItemDataRole.UserRole)

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Postulación",
            "¿Está seguro que desea postularse a esta oferta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                fecha_hoy = date.today().strftime("%Y-%m-%d")
                postulacion = self.service.solicitar_postulacion(
                    self.estudiante_perfil.id_p, id_o, id_e, fecha_hoy
                )
                if postulacion:
                    QMessageBox.information(
                        self.view, "Éxito", "Postulación enviada correctamente."
                    )
                    self.cargar_ofertas()
                    self.cargar_mis_postulaciones()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo registrar la postulación.")
            except (
                RequisitosNoCumplidosError,
                EstudianteConPracticaActivaError,
                CicloNoPermitidoError,
            ) as e:
                if hasattr(self.view, "mostrar_advertencia"):
                    self.view.mostrar_advertencia(str(e))
                else:
                    QMessageBox.critical(self.view, "Error de Requisitos", str(e))
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al procesar: {str(e)}")

    # ==========================================
    # Page 2: Historial de Postulaciones
    # ==========================================
    def cargar_mis_postulaciones(self) -> None:
        tbl = getattr(self.view, "tblMisPostulaciones", None)
        if not tbl:
            return
        try:
            tbl.setRowCount(0)
            postulaciones = self.service.obtener_mis_postulaciones(self.estudiante_perfil.id_p)
            for p in postulaciones:
                row = tbl.rowCount()
                tbl.insertRow(row)

                oferta = self.oferta_repo.buscar_por_id(p.id_o)
                if oferta:
                    try:
                        data = json.loads(oferta.descripcion_oferta)
                        titulo = data.get("titulo", "")
                    except Exception:
                        titulo = oferta.descripcion_oferta
                else:
                    titulo = "N/A"

                emp = self.empresa_repo.buscar_por_id(p.id_e)
                empresa_nombre = emp.nombre_empresa if emp else "N/A"

                estado = (
                    p.estado_de_postulacion.value
                    if hasattr(p.estado_de_postulacion, "value")
                    else p.estado_de_postulacion
                )

                tbl.setItem(row, 0, QTableWidgetItem(str(p.id_o)))
                tbl.setItem(row, 1, QTableWidgetItem(titulo))
                tbl.setItem(row, 2, QTableWidgetItem(empresa_nombre))
                tbl.setItem(row, 3, QTableWidgetItem(estado))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar postulaciones: {str(e)}")

    # ==========================================
    # Page 3: Solicitud de Autorización
    # ==========================================
    def enviar_solicitud(self) -> None:
        txt_name = getattr(self.view, "txtNombreEmpresa", None)
        txt_details = getattr(self.view, "txtDetallesEmpresa", None)
        if not txt_name or not txt_details:
            return

        nombre_empresa = txt_name.text().strip()
        detalles_empresa = txt_details.text().strip()

        if not nombre_empresa or not detalles_empresa:
            QMessageBox.warning(self.view, "Campos vacíos", "Debe ingresar el nombre.")
            return

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Solicitud",
            "¿Está seguro que desea enviar esta solicitud?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                fecha_hoy = date.today().strftime("%Y-%m-%d")
                sol = self.service.registrar_solicitud_autorizacion(
                    self.estudiante_perfil.id_p, nombre_empresa, detalles_empresa, fecha_hoy
                )
                if sol:
                    QMessageBox.information(
                        self.view, "Éxito", "La información fue guardada correctamente."
                    )
                    txt_name.clear()
                    txt_details.clear()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo registrar la solicitud.")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al registrar solicitud: {str(e)}")

    # ==========================================
    # Page 4: Bitácora de Actividades
    # ==========================================
    def cargar_mis_actividades(self) -> None:
        tbl = getattr(self.view, "tblMisActividades", None)
        txa = getattr(self.view, "txaDescripcionActividad", None)
        if not tbl:
            return
        try:
            tbl.setRowCount(0)
            practica = self.service.obtener_practica_activa_estudiante(self.estudiante_perfil.id_p)

            if not practica:
                if txa:
                    txa.setEnabled(False)
                if self.btnGuardarActividad:
                    self.btnGuardarActividad.setEnabled(False)
                return

            if txa:
                txa.setEnabled(True)
            if self.btnGuardarActividad:
                self.btnGuardarActividad.setEnabled(True)

            actividades = self.actividad_repo.listar_por_practica(practica.id_pr)
            for act in actividades:
                row = tbl.rowCount()
                tbl.insertRow(row)

                estado = (
                    act.estado_de_validacion.value
                    if hasattr(act.estado_de_validacion, "value")
                    else act.estado_de_validacion
                )

                tbl.setItem(row, 0, QTableWidgetItem(act.descripcion_de_la_tarea))
                tbl.setItem(row, 1, QTableWidgetItem(estado))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al cargar la bitácora: {str(e)}")

    def guardar_actividad(self) -> None:
        txa = getattr(self.view, "txaDescripcionActividad", None)
        if not txa:
            return

        descripcion = txa.text().strip()
        if not descripcion:
            QMessageBox.warning(self.view, "Campos vacíos", "Debe ingresar el nombre.")
            return

        confirm = QMessageBox.question(
            self.view,
            "Confirmar Actividad",
            "¿Está seguro que desea proponer esta actividad?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                practica = self.service.obtener_practica_activa_estudiante(
                    self.estudiante_perfil.id_p
                )
                if not practica:
                    QMessageBox.warning(
                        self.view, "Bitácora Bloqueada", "No tiene una práctica activa."
                    )
                    return

                act = self.service.registrar_actividad_bitacora(practica.id_pr, descripcion)
                if act:
                    QMessageBox.information(
                        self.view, "Éxito", "La información fue guardada correctamente."
                    )
                    txa.clear()
                    self.cargar_mis_actividades()
                else:
                    QMessageBox.critical(self.view, "Error", "No se pudo proponer la actividad.")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Error al proponer actividad: {str(e)}")

    # ==========================================
    # Legacy Compatibility Methods for Unit Tests
    # ==========================================
    def cargar_catalogo(self) -> None:
        try:
            ofertas = self.service.obtener_catalogo_ofertas(self.estudiante_perfil.id_p)
            if hasattr(self.view, "mostrar_catalogo_ofertas"):
                self.view.mostrar_catalogo_ofertas(ofertas)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))

    def cargar_mis_postulaciones_legacy(self) -> None:
        try:
            postulaciones = self.service.obtener_mis_postulaciones(self.estudiante_perfil.id_p)
            if hasattr(self.view, "mostrar_mis_postulaciones"):
                self.view.mostrar_mis_postulaciones(postulaciones)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))

    def cargar_tramites_legacy(self) -> None:
        try:
            auths = self.service.obtener_mis_solicitudes_autorizacion(self.estudiante_perfil.id_p)
            oficios = self.service.obtener_mis_solicitudes_oficio(self.estudiante_perfil.id_p)
            if hasattr(self.view, "mostrar_mis_solicitudes_autorizacion"):
                self.view.mostrar_mis_solicitudes_autorizacion(auths)
            if hasattr(self.view, "mostrar_mis_solicitudes_oficio"):
                self.view.mostrar_mis_solicitudes_oficio(oficios)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))

    def validar_y_cargar_bitacora(self) -> None:
        try:
            practica = self.service.obtener_practica_activa_estudiante(self.estudiante_perfil.id_p)
            if practica is None:
                if hasattr(self.view, "bloquear_bitacora"):
                    self.view.bloquear_bitacora(True)
                if hasattr(self.view, "mostrar_advertencia"):
                    self.view.mostrar_advertencia(
                        "La bitácora solo es accesible para alumnos con prácticas formalizadas."
                    )
                if hasattr(self.view, "mostrar_mis_actividades"):
                    self.view.mostrar_mis_actividades([])
            else:
                if hasattr(self.view, "bloquear_bitacora"):
                    self.view.bloquear_bitacora(False)
                actividades = self.actividad_repo.listar_por_practica(practica.id_pr)
                if hasattr(self.view, "mostrar_mis_actividades"):
                    self.view.mostrar_mis_actividades(actividades)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al verificar la bitácora: {str(e)}")

    def aplicar_a_vacante(self) -> None:
        try:
            id_o = None
            id_e = None
            if hasattr(self.view, "obtener_oferta_y_empresa_seleccionadas"):
                id_o, id_e = self.view.obtener_oferta_y_empresa_seleccionadas()
            elif hasattr(self.view, "obtener_oferta_seleccionada"):
                id_o = self.view.obtener_oferta_seleccionada()
                oferta = self.oferta_repo.buscar_por_id(id_o)
                if oferta:
                    id_e = oferta.id_e

            if not id_o or not id_e:
                if hasattr(self.view, "mostrar_error"):
                    self.view.mostrar_error("Por favor, seleccione una oferta de la grilla.")
                return

            fecha_hoy = ""
            if hasattr(self.view, "obtener_fecha_actual"):
                fecha_hoy = self.view.obtener_fecha_actual()

            postulacion = self.service.solicitar_postulacion(
                self.estudiante_perfil.id_p, id_o, id_e, fecha_hoy
            )
            if postulacion is not None:
                if hasattr(self.view, "mostrar_exito"):
                    self.view.mostrar_exito("Postulación enviada correctamente.")
                self.cargar_catalogo()
                if hasattr(self.view, "mostrar_mis_postulaciones"):
                    self.cargar_mis_postulaciones_legacy()
        except (RequisitosNoCumplidosError, EstudianteConPracticaActivaError) as e:
            if hasattr(self.view, "mostrar_advertencia"):
                self.view.mostrar_advertencia(str(e))
            elif hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))

    def solicitar_autorizacion(self) -> None:
        try:
            nombre_empresa = ""
            if hasattr(self.view, "txt_nombre_empresa"):
                nombre_empresa = self.view.txt_nombre_empresa.text().strip()
            detalles_empresa = ""
            if hasattr(self.view, "txt_detalles_empresa"):
                detalles_empresa = self.view.txt_detalles_empresa.text().strip()
            fecha = ""
            if hasattr(self.view, "obtener_fecha_actual"):
                fecha = self.view.obtener_fecha_actual()

            sol = self.service.registrar_solicitud_autorizacion(
                self.estudiante_perfil.id_p, nombre_empresa, detalles_empresa, fecha
            )
            if sol is not None:
                if hasattr(self.view, "mostrar_exito"):
                    self.view.mostrar_exito("Solicitud de autorización registrada exitosamente.")
                self.cargar_tramites_legacy()
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))

    def solicitar_oficio(self) -> None:
        try:
            destinatario = ""
            if hasattr(self.view, "txt_destinatario"):
                destinatario = self.view.txt_destinatario.text().strip()
            cargo = ""
            if hasattr(self.view, "txt_cargo"):
                cargo = self.view.txt_cargo.text().strip()
            nombre_empresa = ""
            if hasattr(self.view, "txt_nombre_empresa_oficio"):
                nombre_empresa = self.view.txt_nombre_empresa_oficio.text().strip()
            fecha = ""
            if hasattr(self.view, "obtener_fecha_actual"):
                fecha = self.view.obtener_fecha_actual()

            sol = self.service.registrar_solicitud_oficio(
                self.estudiante_perfil.id_p, destinatario, cargo, nombre_empresa, fecha
            )
            if sol is not None:
                if hasattr(self.view, "mostrar_exito"):
                    self.view.mostrar_exito("Solicitud de oficio registrada exitosamente.")
                self.cargar_tramites_legacy()
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))

    def registrar_actividad_bitacora(self) -> None:
        try:
            practica = self.service.obtener_practica_activa_estudiante(self.estudiante_perfil.id_p)
            if practica is None:
                return
            descripcion = ""
            if hasattr(self.view, "txt_descripcion_bitacora"):
                descripcion = self.view.txt_descripcion_bitacora.text().strip()
            act = self.service.registrar_actividad_bitacora(practica.id_pr, descripcion)
            if act is not None:
                if hasattr(self.view, "mostrar_exito"):
                    self.view.mostrar_exito("Actividad registrada exitosamente.")
                self.validar_y_cargar_bitacora()
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))

    # ==========================================
    # Help Dialogs
    # ==========================================
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
