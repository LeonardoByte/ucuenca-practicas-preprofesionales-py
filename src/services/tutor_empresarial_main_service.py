from datetime import datetime
from typing import Optional

from src.models import (
    Actividad,
    Empresa,
    EstadoFirmaFormulario,
    Practica,
    TipoFormulario,
)
from src.repositories import EmpresaRepository
from src.services.exceptions import EvaluacionTempranaError
from src.services.interfaces.tutor_empresarial_main_service_abc import (
    TutorEmpresarialMainServiceABC,
)
from src.services.practica_service import PracticaService


class TutorEmpresarialMainService(TutorEmpresarialMainServiceABC):
    def __init__(
        self,
        practica_service: Optional[PracticaService] = None,
        empresa_repo: Optional[EmpresaRepository] = None,
    ) -> None:
        self.practica_service = practica_service or PracticaService()
        self.empresa_repo = empresa_repo or EmpresaRepository()

    def registrar_evaluacion_formulario3(
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
            tipo_formulario=TipoFormulario.FORMULARIO_3,
            estado_firma=estado_de_firma,
            fecha_entrega=fecha_de_entrega_registro,
            numero_formulario="FORM-03",
        )
        return form is not None

    def obtener_datos_empresa_tutor(self, id_e: int) -> Optional[Empresa]:
        return self.empresa_repo.buscar_por_id(id_e)

    def obtener_practicas_tutor_emp(self, id_p_tutor_emp: int) -> list[Practica]:
        self.practica_service.practica_repo._cargar_datos()
        return [
            p for p in self.practica_service.practica_repo._datos
            if p.id_p_tutor_emp == id_p_tutor_emp
        ]

    def proponer_actividad_practica(self, id_pr: int, descripcion: str) -> Optional[Actividad]:
        return self.practica_service.registrar_actividad(id_pr, descripcion)
