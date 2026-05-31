from PyQt6.QtCore import QObject, pyqtSignal

from src.services.exceptions import DocumentacionIncompletaError
from src.services.interfaces.coordinador_main_service_abc import CoordinadorMainServiceABC


class CoordinadorController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: CoordinadorMainServiceABC, coordinador_perfil) -> None:
        super().__init__()
        self.view = view
        self.service = service
        self.coordinador_perfil = coordinador_perfil

        # Hook navigation
        if hasattr(self.view, "btn_nav_postulaciones") and self.view.btn_nav_postulaciones:
            self.view.btn_nav_postulaciones.clicked.connect(self.ir_a_postulaciones)
        if hasattr(self.view, "btn_nav_tramites") and self.view.btn_nav_tramites:
            self.view.btn_nav_tramites.clicked.connect(self.ir_a_tramites)
        if hasattr(self.view, "btn_nav_supervision") and self.view.btn_nav_supervision:
            self.view.btn_nav_supervision.clicked.connect(self.ir_a_supervision)
        if hasattr(self.view, "btn_cerrar_sesion") and self.view.btn_cerrar_sesion:
            self.view.btn_cerrar_sesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Hook actions
        if hasattr(self.view, "btn_validar_requisitos") and self.view.btn_validar_requisitos:
            self.view.btn_validar_requisitos.clicked.connect(self.validar_requisitos)
        if hasattr(self.view, "btn_rechazar_requisitos") and self.view.btn_rechazar_requisitos:
            self.view.btn_rechazar_requisitos.clicked.connect(self.rechazar_requisitos)
        if hasattr(self.view, "btn_enviar_terna") and self.view.btn_enviar_terna:
            self.view.btn_enviar_terna.clicked.connect(self.enviar_terna)
        if hasattr(self.view, "btn_aprobar_autorizacion") and self.view.btn_aprobar_autorizacion:
            self.view.btn_aprobar_autorizacion.clicked.connect(self.aprobar_autorizacion)
        if hasattr(self.view, "btn_rechazar_autorizacion") and self.view.btn_rechazar_autorizacion:
            self.view.btn_rechazar_autorizacion.clicked.connect(self.rechazar_autorizacion)
        if hasattr(self.view, "btn_emitir_oficio") and self.view.btn_emitir_oficio:
            self.view.btn_emitir_oficio.clicked.connect(self.emitir_oficio)
        if hasattr(self.view, "btn_asignar_tutor") and self.view.btn_asignar_tutor:
            self.view.btn_asignar_tutor.clicked.connect(self.asignar_tutor)
        if hasattr(self.view, "btn_aprobar_cierre") and self.view.btn_aprobar_cierre:
            self.view.btn_aprobar_cierre.clicked.connect(self.aprobar_cierre)

        # Initial load
        self.cargar_postulaciones_y_ofertas()
        self.cargar_tramites()
        self.cargar_supervision()

    def ir_a_postulaciones(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("postulaciones")
        self.cargar_postulaciones_y_ofertas()

    def ir_a_tramites(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("tramites")
        self.cargar_tramites()

    def ir_a_supervision(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("supervision")
        self.cargar_supervision()

    def solicitar_cerrar_sesion(self) -> None:
        if hasattr(self.view, "confirmar_accion"):
            if not self.view.confirmar_accion("¿Está seguro de cerrar sesión?"):
                return
        self.cerrar_sesion.emit()

    def cargar_postulaciones_y_ofertas(self) -> None:
        try:
            postulaciones = self.service.revisar_postulaciones_pendientes()
            ofertas = self.service.listar_ofertas_con_conteo_validadas()
            if hasattr(self.view, "mostrar_postulaciones_pendientes"):
                self.view.mostrar_postulaciones_pendientes(postulaciones)
            if hasattr(self.view, "mostrar_ofertas_conteo"):
                self.view.mostrar_ofertas_conteo(ofertas)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar postulaciones u ofertas: {str(e)}")

    def cargar_tramites(self) -> None:
        try:
            auths = self.service.listar_solicitudes_autorizacion_pendientes()
            oficios = self.service.listar_solicitudes_oficio_pendientes()
            if hasattr(self.view, "mostrar_solicitudes_autorizacion"):
                self.view.mostrar_solicitudes_autorizacion(auths)
            if hasattr(self.view, "mostrar_solicitudes_oficio"):
                self.view.mostrar_solicitudes_oficio(oficios)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar trámites: {str(e)}")

    def cargar_supervision(self) -> None:
        try:
            practicas = self.service.listar_practicas_pendientes_de_tutor(
                self.coordinador_perfil.id_p
            )
            if hasattr(self.view, "mostrar_practicas_pendientes_tutor"):
                self.view.mostrar_practicas_pendientes_tutor(practicas)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar supervisión: {str(e)}")

    def validar_requisitos(self) -> None:
        self._evaluar_requisitos(True)

    def rechazar_requisitos(self) -> None:
        self._evaluar_requisitos(False)

    def _evaluar_requisitos(self, aprobado: bool) -> None:
        try:
            id_pos = None
            if hasattr(self.view, "obtener_postulacion_seleccionada"):
                id_pos = self.view.obtener_postulacion_seleccionada()

            if not id_pos:
                self.view.mostrar_error("Por favor, seleccione una postulación.")
                return

            success = self.service.validar_requisitos_alumno(id_pos, aprobado)
            if success:
                accion = "validada" if aprobado else "rechazada"
                self.view.mostrar_exito(f"Postulación {accion} exitosamente.")
                self.cargar_postulaciones_y_ofertas()
            else:
                self.view.mostrar_error("No se pudo procesar la postulación.")
        except Exception as e:
            self.view.mostrar_error(f"Error al procesar requisitos: {str(e)}")

    def enviar_terna(self) -> None:
        try:
            id_postulaciones = []
            if hasattr(self.view, "obtener_postulaciones_terna_seleccionadas"):
                id_postulaciones = self.view.obtener_postulaciones_terna_seleccionadas()

            if not id_postulaciones or len(id_postulaciones) != 3:
                self.view.mostrar_error(
                    "Debe seleccionar exactamente 3 postulaciones para enviar una terna."
                )
                return

            success = self.service.enviar_terna_a_empresa(id_postulaciones)
            if success:
                self.view.mostrar_exito("Terna agrupada y despachada a la empresa exitosamente.")
                self.cargar_postulaciones_y_ofertas()
            else:
                self.view.mostrar_error("No se pudo enviar la terna.")
        except Exception as e:
            self.view.mostrar_error(f"Error al enviar terna: {str(e)}")

    def aprobar_autorizacion(self) -> None:
        self._evaluar_autorizacion(True)

    def rechazar_autorizacion(self) -> None:
        self._evaluar_autorizacion(False)

    def _evaluar_autorizacion(self, aprobado: bool) -> None:
        try:
            id_sol_aut = None
            if hasattr(self.view, "obtener_solicitud_autorizacion_seleccionada"):
                id_sol_aut = self.view.obtener_solicitud_autorizacion_seleccionada()

            if not id_sol_aut:
                self.view.mostrar_error("Por favor, seleccione una solicitud de autorización.")
                return

            nombre_dest = ""
            if hasattr(self.view, "txt_nombre_destinatario"):
                nombre_dest = self.view.txt_nombre_destinatario.text().strip()

            cargo_dest = ""
            if hasattr(self.view, "txt_cargo_destinatario"):
                cargo_dest = self.view.txt_cargo_destinatario.text().strip()

            success = self.service.evaluar_solicitud_autorizacion(
                id_sol_aut, aprobado, self.coordinador_perfil.id_p, nombre_dest, cargo_dest
            )
            if success:
                accion = "aprobada" if aprobado else "rechazada"
                self.view.mostrar_exito(f"Solicitud de autorización {accion} exitosamente.")
                if hasattr(self.view, "txt_nombre_destinatario"):
                    self.view.txt_nombre_destinatario.clear()
                if hasattr(self.view, "txt_cargo_destinatario"):
                    self.view.txt_cargo_destinatario.clear()
                self.cargar_tramites()
            else:
                self.view.mostrar_error("No se pudo evaluar la solicitud.")
        except Exception as e:
            self.view.mostrar_error(f"Error al evaluar autorización: {str(e)}")

    def emitir_oficio(self) -> None:
        try:
            id_sol_of = None
            if hasattr(self.view, "obtener_solicitud_oficio_seleccionada"):
                id_sol_of = self.view.obtener_solicitud_oficio_seleccionada()

            if not id_sol_of:
                self.view.mostrar_error("Por favor, seleccione una solicitud de oficio.")
                return

            ruta_pdf = ""
            if hasattr(self.view, "obtener_ruta_oficio_pdf"):
                ruta_pdf = self.view.obtener_ruta_oficio_pdf()

            if not ruta_pdf:
                self.view.mostrar_error("Por favor, especifique la ruta de destino del oficio PDF.")
                return

            success = self.service.procesar_emision_oficio(
                id_sol_of, self.coordinador_perfil.id_p, ruta_pdf
            )
            if success:
                self.view.mostrar_exito("Oficio emitido y firmado digitalmente.")
                self.cargar_tramites()
            else:
                self.view.mostrar_error("No se pudo emitir el oficio.")
        except Exception as e:
            self.view.mostrar_error(f"Error al emitir oficio: {str(e)}")

    def asignar_tutor(self) -> None:
        try:
            id_pr = None
            if hasattr(self.view, "obtener_practica_seleccionada"):
                id_pr = self.view.obtener_practica_seleccionada()

            id_tutor = None
            if hasattr(self.view, "obtener_tutor_academico_seleccionado"):
                id_tutor = self.view.obtener_tutor_academico_seleccionado()

            if not id_pr or not id_tutor:
                self.view.mostrar_error("Debe seleccionar una práctica y un tutor docente.")
                return

            success = self.service.asignar_tutor_a_practica(id_pr, id_tutor)
            if success:
                self.view.mostrar_exito("Tutor académico asignado correctamente.")
                self.cargar_supervision()
            else:
                self.view.mostrar_error("No se pudo asignar el tutor.")
        except Exception as e:
            self.view.mostrar_error(f"Error al asignar tutor: {str(e)}")

    def aprobar_cierre(self) -> None:
        try:
            id_pr = None
            if hasattr(self.view, "obtener_practica_seleccionada"):
                id_pr = self.view.obtener_practica_seleccionada()

            if not id_pr:
                self.view.mostrar_error("Por favor, seleccione una práctica.")
                return

            success = self.service.ejecutar_cierre_oficial_practica(id_pr)
            if success:
                self.view.mostrar_exito(
                    "Cierre oficial aprobado. Expediente culminado exitosamente."
                )
                self.cargar_supervision()
            else:
                self.view.mostrar_error("No se pudo realizar el cierre oficial de la práctica.")
        except DocumentacionIncompletaError as e:
            if hasattr(self.view, "mostrar_advertencia"):
                self.view.mostrar_advertencia(str(e))
            elif hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))
        except Exception as e:
            self.view.mostrar_error(f"Error al procesar cierre: {str(e)}")
