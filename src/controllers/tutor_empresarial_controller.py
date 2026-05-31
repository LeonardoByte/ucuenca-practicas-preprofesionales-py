from PyQt6.QtCore import QObject, pyqtSignal

from src.models.estados import EstadoFirmaFormulario
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

        # Hook navigation
        if hasattr(self.view, "btn_nav_practicantes") and self.view.btn_nav_practicantes:
            self.view.btn_nav_practicantes.clicked.connect(self.ir_a_practicantes)
        if hasattr(self.view, "btn_nav_empresa") and self.view.btn_nav_empresa:
            self.view.btn_nav_empresa.clicked.connect(self.ir_a_empresa)
        if hasattr(self.view, "btn_cerrar_sesion") and self.view.btn_cerrar_sesion:
            self.view.btn_cerrar_sesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Hook actions
        if hasattr(self.view, "btn_proponer_actividad") and self.view.btn_proponer_actividad:
            self.view.btn_proponer_actividad.clicked.connect(self.proponer_actividad)
        if hasattr(self.view, "btn_evaluar_f3") and self.view.btn_evaluar_f3:
            self.view.btn_evaluar_f3.clicked.connect(self.evaluar_formulario3)

        # Initial load
        self.cargar_datos_empresa()
        self.cargar_practicas()

    def ir_a_practicantes(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("practicantes")
        self.cargar_practicas()

    def ir_a_empresa(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("empresa")

    def solicitar_cerrar_sesion(self) -> None:
        if hasattr(self.view, "confirmar_accion"):
            if not self.view.confirmar_accion("¿Está seguro de cerrar sesión?"):
                return
        self.cerrar_sesion.emit()

    def cargar_datos_empresa(self) -> None:
        try:
            empresa = self.service.obtener_datos_empresa_tutor(self.tutor_perfil.id_e)
            if empresa and hasattr(self.view, "mostrar_perfil_empresa"):
                self.view.mostrar_perfil_empresa(empresa)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al obtener datos de empresa: {str(e)}")

    def cargar_practicas(self) -> None:
        try:
            practicas = self.service.obtener_practicas_tutor_emp(self.tutor_perfil.id_p)
            if hasattr(self.view, "mostrar_practicas"):
                self.view.mostrar_practicas(practicas)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar practicantes: {str(e)}")

    def proponer_actividad(self) -> None:
        try:
            id_pr = None
            if hasattr(self.view, "obtener_practica_seleccionada"):
                id_pr = self.view.obtener_practica_seleccionada()

            if not id_pr:
                self.view.mostrar_error("Por favor, seleccione un estudiante/práctica.")
                return

            descripcion = ""
            if hasattr(self.view, "txt_descripcion_actividad"):
                descripcion = self.view.txt_descripcion_actividad.text().strip()

            if not descripcion:
                self.view.mostrar_error("Por favor, ingrese la descripción de la tarea.")
                return

            actividad = self.service.proponer_actividad_practica(id_pr, descripcion)
            if actividad is not None:
                self.view.mostrar_exito("Actividad propuesta con éxito.")
                if hasattr(self.view, "txt_descripcion_actividad"):
                    self.view.txt_descripcion_actividad.clear()
                # Refresh activities list if the view supports it
                if hasattr(self.view, "mostrar_actividades"):
                    # Retrieve updated activities
                    from src.repositories import ActividadRepository
                    repo = ActividadRepository()
                    self.view.mostrar_actividades(repo.listar_por_practica(id_pr))
            else:
                self.view.mostrar_error("No se pudo proponer la actividad.")
        except Exception as e:
            self.view.mostrar_error(f"Error al proponer actividad: {str(e)}")

    def evaluar_formulario3(self) -> None:
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

            success = self.service.registrar_evaluacion_formulario3(
                id_pr, estado_firma, fecha_entrega
            )
            if success:
                self.view.mostrar_exito("Evaluación (Formulario 3) registrada exitosamente.")
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
