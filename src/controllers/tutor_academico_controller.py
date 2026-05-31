from PyQt6.QtCore import QObject, pyqtSignal

from src.models.estados import EstadoFirmaFormulario, EstadoValidacionActividad
from src.services.exceptions import EvaluacionTempranaError
from src.services.interfaces.tutor_academico_main_service_abc import TutorAcademicoMainServiceABC


class TutorAcademicoController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: TutorAcademicoMainServiceABC, tutor_perfil) -> None:
        super().__init__()
        self.view = view
        self.service = service
        self.tutor_perfil = tutor_perfil

        # Hook navigation
        if hasattr(self.view, "btn_nav_estudiantes") and self.view.btn_nav_estudiantes:
            self.view.btn_nav_estudiantes.clicked.connect(self.ir_a_estudiantes)
        if hasattr(self.view, "btn_cerrar_sesion") and self.view.btn_cerrar_sesion:
            self.view.btn_cerrar_sesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Hook actions
        if hasattr(self.view, "btn_auditar_bitacora") and self.view.btn_auditar_bitacora:
            self.view.btn_auditar_bitacora.clicked.connect(self.cargar_bitacora)
        if hasattr(self.view, "btn_validar_actividad") and self.view.btn_validar_actividad:
            self.view.btn_validar_actividad.clicked.connect(self.validar_actividad)
        if hasattr(self.view, "btn_rechazar_actividad") and self.view.btn_rechazar_actividad:
            self.view.btn_rechazar_actividad.clicked.connect(self.rechazar_actividad)
        if hasattr(self.view, "btn_evaluar_f2") and self.view.btn_evaluar_f2:
            self.view.btn_evaluar_f2.clicked.connect(self.evaluar_formulario2)

        # Initial load
        self.cargar_practicas()

    def ir_a_estudiantes(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("estudiantes")
        self.cargar_practicas()

    def solicitar_cerrar_sesion(self) -> None:
        if hasattr(self.view, "confirmar_accion"):
            if not self.view.confirmar_accion("¿Está seguro de cerrar sesión?"):
                return
        self.cerrar_sesion.emit()

    def cargar_practicas(self) -> None:
        try:
            practicas = self.service.obtener_practicas_tutor_acad(self.tutor_perfil.id_p)
            if hasattr(self.view, "mostrar_practicas"):
                self.view.mostrar_practicas(practicas)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar practicantes: {str(e)}")

    def cargar_bitacora(self) -> None:
        try:
            id_pr = None
            if hasattr(self.view, "obtener_practica_seleccionada"):
                id_pr = self.view.obtener_practica_seleccionada()

            if not id_pr:
                self.view.mostrar_error("Por favor, seleccione un estudiante/práctica.")
                return

            actividades = self.service.listar_actividades_de_practica(id_pr)
            if hasattr(self.view, "mostrar_seccion"):
                self.view.mostrar_seccion("bitacora")
            if hasattr(self.view, "mostrar_actividades"):
                self.view.mostrar_actividades(actividades)
        except Exception as e:
            self.view.mostrar_error(f"Error al cargar bitácora: {str(e)}")

    def validar_actividad(self) -> None:
        self._evaluar_actividad(EstadoValidacionActividad.VALIDADA)

    def rechazar_actividad(self) -> None:
        self._evaluar_actividad(EstadoValidacionActividad.RECHAZADA)

    def _evaluar_actividad(self, estado: EstadoValidacionActividad) -> None:
        try:
            id_pr = None
            if hasattr(self.view, "obtener_practica_seleccionada"):
                id_pr = self.view.obtener_practica_seleccionada()

            id_act = None
            if hasattr(self.view, "obtener_actividad_seleccionada"):
                id_act = self.view.obtener_actividad_seleccionada()

            if not id_pr or not id_act:
                self.view.mostrar_error("Debe seleccionar la práctica y la actividad a evaluar.")
                return

            success = self.service.evaluar_actividad_alumno(id_act, id_pr, estado)
            if success:
                accion = "validada" if estado == EstadoValidacionActividad.VALIDADA else "rechazada"
                self.view.mostrar_exito(f"Actividad {accion} correctamente.")
                # Refresh list
                actividades = self.service.listar_actividades_de_practica(id_pr)
                if hasattr(self.view, "mostrar_actividades"):
                    self.view.mostrar_actividades(actividades)
            else:
                self.view.mostrar_error("No se pudo evaluar la actividad.")
        except Exception as e:
            self.view.mostrar_error(f"Error al evaluar actividad: {str(e)}")

    def evaluar_formulario2(self) -> None:
        try:
            id_pr = None
            if hasattr(self.view, "obtener_practica_seleccionada"):
                id_pr = self.view.obtener_practica_seleccionada()

            if not id_pr:
                self.view.mostrar_error("Por favor, seleccione un estudiante/práctica.")
                return

            estado_firma = EstadoFirmaFormulario.COMPLETADO
            if hasattr(self.view, "obtener_estado_firma_evaluacion"):
                estado_firma = self.view.obtener_estado_firma_evaluacion()

            fecha_entrega = ""
            if hasattr(self.view, "obtener_fecha_evaluacion"):
                fecha_entrega = self.view.obtener_fecha_evaluacion()

            if not fecha_entrega:
                self.view.mostrar_error("Por favor, ingrese la fecha de la evaluación.")
                return

            success = self.service.registrar_evaluacion_formulario2(
                id_pr, estado_firma, fecha_entrega
            )
            if success:
                self.view.mostrar_exito("Evaluación (Formulario 2) registrada exitosamente.")
                self.cargar_practicas()
            else:
                self.view.mostrar_error("No se pudo registrar la evaluación.")
        except EvaluacionTempranaError as e:
            if hasattr(self.view, "mostrar_advertencia"):
                self.view.mostrar_advertencia(str(e))
            elif hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(str(e))
        except Exception as e:
            self.view.mostrar_error(f"Error al registrar evaluación: {str(e)}")
