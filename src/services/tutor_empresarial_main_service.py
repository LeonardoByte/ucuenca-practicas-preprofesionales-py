from typing import Optional

from src.services.interfaces.tutor_empresarial_main_service_abc import (
    TutorEmpresarialMainServiceABC,
)
from src.services.practica_service import PracticaService


class TutorEmpresarialMainService(TutorEmpresarialMainServiceABC):
    def __init__(self, practica_service: Optional[PracticaService] = None) -> None:
        self.practica_service = practica_service or PracticaService()

    def registrar_evaluacion_formulario3(
        self,
        id_pr: int,
        estado_de_firma: str,
        fecha_de_entrega_registro: str,
        numero_formulario: str
    ) -> bool:
        form = self.practica_service.actualizar_formulario(
            id_pr=id_pr,
            tipo_formulario="Formulario 3",
            estado_firma=estado_de_firma,
            fecha_entrega=fecha_de_entrega_registro,
            numero_formulario=numero_formulario
        )
        return form is not None
