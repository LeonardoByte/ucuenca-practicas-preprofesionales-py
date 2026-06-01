from PyQt6.QtCore import QObject, pyqtSignal

from src.repositories import ActividadRepository, OfertaRepository
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

        # Hook navigation
        if hasattr(self.view, "btn_nav_catalogo") and self.view.btn_nav_catalogo:
            self.view.btn_nav_catalogo.clicked.connect(self.ir_a_catalogo)
        if hasattr(self.view, "btn_nav_postulaciones") and self.view.btn_nav_postulaciones:
            self.view.btn_nav_postulaciones.clicked.connect(self.ir_a_postulaciones)
        if hasattr(self.view, "btn_nav_tramites") and self.view.btn_nav_tramites:
            self.view.btn_nav_tramites.clicked.connect(self.ir_a_tramites)
        if hasattr(self.view, "btn_nav_bitacora") and self.view.btn_nav_bitacora:
            self.view.btn_nav_bitacora.clicked.connect(self.ir_a_bitacora)
        if hasattr(self.view, "btn_cerrar_sesion") and self.view.btn_cerrar_sesion:
            self.view.btn_cerrar_sesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Hook actions
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

        # Initial load
        self.cargar_catalogo()
        self.cargar_postulaciones()
        self.cargar_tramites()

    def ir_a_catalogo(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("catalogo")
        self.cargar_catalogo()

    def ir_a_postulaciones(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("postulaciones")
        self.cargar_postulaciones()

    def ir_a_tramites(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("tramites")
        self.cargar_tramites()

    def ir_a_bitacora(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("bitacora")
        self.validar_y_cargar_bitacora()

    def solicitar_cerrar_sesion(self) -> None:
        if hasattr(self.view, "confirmar_accion"):
            if not self.view.confirmar_accion("¿Está seguro de cerrar sesión?"):
                return
        self.cerrar_sesion.emit()

    def cargar_catalogo(self) -> None:
        try:
            ofertas = self.service.obtener_catalogo_ofertas(self.estudiante_perfil.id_p)
            if hasattr(self.view, "mostrar_catalogo_ofertas"):
                self.view.mostrar_catalogo_ofertas(ofertas)
        except CicloNoPermitidoError as e:
            if hasattr(self.view, "mostrar_catalogo_ofertas"):
                self.view.mostrar_catalogo_ofertas([])
            if hasattr(self.view, "mostrar_advertencia"):
                self.view.mostrar_advertencia(str(e))
            elif hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al obtener catálogo: {str(e)}")

    def cargar_postulaciones(self) -> None:
        try:
            postulaciones = self.service.obtener_mis_postulaciones(self.estudiante_perfil.id_p)
            if hasattr(self.view, "mostrar_mis_postulaciones"):
                self.view.mostrar_mis_postulaciones(postulaciones)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar postulaciones: {str(e)}")

    def cargar_tramites(self) -> None:
        try:
            auths = self.service.obtener_mis_solicitudes_autorizacion(self.estudiante_perfil.id_p)
            oficios = self.service.obtener_mis_solicitudes_oficio(self.estudiante_perfil.id_p)
            if hasattr(self.view, "mostrar_mis_solicitudes_autorizacion"):
                self.view.mostrar_mis_solicitudes_autorizacion(auths)
            if hasattr(self.view, "mostrar_mis_solicitudes_oficio"):
                self.view.mostrar_mis_solicitudes_oficio(oficios)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar trámites: {str(e)}")

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
                act_repo = ActividadRepository()
                actividades = act_repo.listar_por_practica(practica.id_pr)
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
                # Lookup company id from offer repo
                o_repo = OfertaRepository()
                oferta = o_repo.buscar_por_id(id_o)
                if oferta:
                    id_e = oferta.id_e

            if not id_o or not id_e:
                self.view.mostrar_error("Por favor, seleccione una oferta de la grilla.")
                return

            fecha_hoy = ""
            if hasattr(self.view, "obtener_fecha_actual"):
                fecha_hoy = self.view.obtener_fecha_actual()

            if not fecha_hoy:
                self.view.mostrar_error("No se pudo obtener la fecha de postulación.")
                return

            postulacion = self.service.solicitar_postulacion(
                self.estudiante_perfil.id_p, id_o, id_e, fecha_hoy
            )
            if postulacion is not None:
                self.view.mostrar_exito("Postulación enviada correctamente.")
                self.cargar_catalogo()
                self.cargar_postulaciones()
            else:
                self.view.mostrar_error("No se pudo registrar la postulación.")
        except (RequisitosNoCumplidosError, EstudianteConPracticaActivaError) as e:
            if hasattr(self.view, "mostrar_advertencia"):
                self.view.mostrar_advertencia(str(e))
            elif hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))
        except Exception as e:
            self.view.mostrar_error(f"Error al postular: {str(e)}")

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

            if not nombre_empresa or not detalles_empresa or not fecha:
                self.view.mostrar_error("Por favor complete todos los datos del formulario.")
                return

            sol = self.service.registrar_solicitud_autorizacion(
                self.estudiante_perfil.id_p, nombre_empresa, detalles_empresa, fecha
            )
            if sol is not None:
                self.view.mostrar_exito("Solicitud de autorización registrada exitosamente.")
                if hasattr(self.view, "txt_nombre_empresa"):
                    self.view.txt_nombre_empresa.clear()
                if hasattr(self.view, "txt_detalles_empresa"):
                    self.view.txt_detalles_empresa.clear()
                self.cargar_tramites()
            else:
                self.view.mostrar_error("No se pudo registrar la solicitud.")
        except Exception as e:
            self.view.mostrar_error(f"Error al registrar solicitud: {str(e)}")

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

            if not destinatario or not cargo or not nombre_empresa or not fecha:
                self.view.mostrar_error("Por favor complete todos los datos del oficio.")
                return

            sol = self.service.registrar_solicitud_oficio(
                self.estudiante_perfil.id_p, destinatario, cargo, nombre_empresa, fecha
            )
            if sol is not None:
                self.view.mostrar_exito(
                    "Solicitud de oficio de certificación registrada exitosamente."
                )
                if hasattr(self.view, "txt_destinatario"):
                    self.view.txt_destinatario.clear()
                if hasattr(self.view, "txt_cargo"):
                    self.view.txt_cargo.clear()
                if hasattr(self.view, "txt_nombre_empresa_oficio"):
                    self.view.txt_nombre_empresa_oficio.clear()
                self.cargar_tramites()
            else:
                self.view.mostrar_error("No se pudo registrar la solicitud.")
        except Exception as e:
            self.view.mostrar_error(f"Error al registrar solicitud de oficio: {str(e)}")

    def registrar_actividad_bitacora(self) -> None:
        try:
            practica = self.service.obtener_practica_activa_estudiante(self.estudiante_perfil.id_p)
            if practica is None:
                self.view.mostrar_error(
                    "No posee ninguna práctica activa para registrar actividades."
                )
                return

            descripcion = ""
            if hasattr(self.view, "txt_descripcion_bitacora"):
                descripcion = self.view.txt_descripcion_bitacora.text().strip()

            if not descripcion:
                self.view.mostrar_error("La descripción de la tarea no puede estar vacía.")
                return

            actividad = self.service.registrar_actividad_bitacora(practica.id_pr, descripcion)
            if actividad is not None:
                self.view.mostrar_exito("Actividad registrada en la bitácora correctamente.")
                if hasattr(self.view, "txt_descripcion_bitacora"):
                    self.view.txt_descripcion_bitacora.clear()
                self.validar_y_cargar_bitacora()
            else:
                self.view.mostrar_error("No se pudo registrar la actividad.")
        except Exception as e:
            self.view.mostrar_error(f"Error al registrar actividad en bitácora: {str(e)}")
