from typing import Optional

from src.models import Oferta, Postulacion
from src.services.interfaces.empresa_main_service_abc import EmpresaMainServiceABC
from src.services.oferta_service import OfertaService
from src.services.postulacion_service import PostulacionService
from src.services.practica_service import PracticaService


class EmpresaMainService(EmpresaMainServiceABC):
    def __init__(
        self,
        oferta_service: Optional[OfertaService] = None,
        postulacion_service: Optional[PostulacionService] = None,
        practica_service: Optional[PracticaService] = None,
    ) -> None:
        self.oferta_service = oferta_service or OfertaService()
        self.postulacion_service = postulacion_service or PostulacionService()
        self.practica_service = practica_service or PracticaService()

    def registrar_oferta(
        self,
        id_e: int,
        descripcion_oferta: str,
        requisitos: str,
        fecha_de_publicacion: str,
        duracion: str,
        remuneracion: float,
    ) -> Optional[Oferta]:
        return self.oferta_service.crear_oferta(
            id_e, descripcion_oferta, requisitos, fecha_de_publicacion, duracion, remuneracion
        )

    def visualizar_terna_recibida(self, id_terna: int) -> list[Postulacion]:
        return self.postulacion_service.listar_por_id_terna(id_terna)

    def seleccionar_candidato_ganador(
        self, id_pos_aceptada: int, id_p_tutor_emp: int, fecha_inicio: str, fecha_fin: str
    ) -> bool:
        practica = self.practica_service.formalizar_practica(
            id_pos_aceptada, id_p_tutor_emp, fecha_inicio, fecha_fin
        )
        return practica is not None
