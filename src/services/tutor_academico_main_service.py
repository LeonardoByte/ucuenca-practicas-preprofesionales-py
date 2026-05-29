from typing import Optional

from src.services.interfaces.tutor_academico_main_service_abc import TutorAcademicoMainServiceABC
from src.services.practica_service import PracticaService


class TutorAcademicoMainService(TutorAcademicoMainServiceABC):
    def __init__(self, practica_service: Optional[PracticaService] = None) -> None:
        self.practica_service = practica_service or PracticaService()

    def evaluar_actividad_alumno(self, id_act: int, id_pr: int, estado: str) -> bool:
        return self.practica_service.evaluar_actividad(id_act, id_pr, estado)

    def registrar_evaluacion_formulario2(
        self,
        id_pr: int,
        estado_de_firma: str,
        fecha_de_entrega_registro: str,
        numero_formulario: str
    ) -> bool:
        form = self.practica_service.actualizar_formulario(
            id_pr=id_pr,
            tipo_formulario="Formulario 2",
            estado_firma=estado_de_firma,
            fecha_entrega=fecha_de_entrega_registro,
            numero_formulario=numero_formulario
        )
        return form is not None
