from datetime import datetime
from typing import Optional

from src.models import (
    Actividad,
    EstadoFirmaFormulario,
    EstadoValidacionActividad,
    Practica,
    TipoFormulario,
)
from src.services.exceptions import EvaluacionTempranaError
from src.services.interfaces.tutor_academico_main_service_abc import TutorAcademicoMainServiceABC
from src.services.practica_service import PracticaService


class TutorAcademicoMainService(TutorAcademicoMainServiceABC):
    def __init__(self, practica_service: Optional[PracticaService] = None) -> None:
        self.practica_service = practica_service or PracticaService()

    def evaluar_actividad_alumno(
        self, id_act: int, id_pr: int, estado: EstadoValidacionActividad
    ) -> bool:
        return self.practica_service.evaluar_actividad(id_act, id_pr, estado)

    def registrar_evaluacion_formulario2(
        self, id_pr: int, estado_de_firma: EstadoFirmaFormulario, fecha_de_entrega_registro: str
    ) -> bool:
        practica = self.practica_service.practica_repo.buscar_por_id(id_pr)
        if not practica:
            return False

        # Validación temporal perimetral (Módulo 6)
        fecha_fin_dt = datetime.strptime(practica.fecha_fin, "%Y-%m-%d").date()
        fecha_entrega_dt = datetime.strptime(fecha_de_entrega_registro, "%Y-%m-%d").date()
        if (fecha_fin_dt - fecha_entrega_dt).days > 7:
            raise EvaluacionTempranaError(
                "No se puede registrar la evaluación final con más de 7 días "
                "de anticipación al término de la práctica."
            )

        form = self.practica_service.actualizar_formulario(
            id_pr=id_pr,
            tipo_formulario=TipoFormulario.FORMULARIO_2,
            estado_firma=estado_de_firma,
            fecha_entrega=fecha_de_entrega_registro,
            numero_formulario="FORM-02",
        )
        return form is not None

    def obtener_practicas_tutor_acad(self, id_p_tutor_acad: int) -> list[Practica]:
        self.practica_service.practica_repo._cargar_datos()
        return [
            p for p in self.practica_service.practica_repo._datos
            if p.id_p_tutor_acad == id_p_tutor_acad
        ]

    def listar_actividades_de_practica(self, id_pr: int) -> list[Actividad]:
        return self.practica_service.actividad_repo.listar_por_practica(id_pr)

