from typing import Optional

from src.models import (
    Convenio,
    EstadoConvenio,
    EstadoPractica,
    Oferta,
    Postulacion,
    Practica,
    TutorEmpresarial,
    EstadoPostulacion,
)
from src.repositories import ConvenioRepository, TutorEmpresarialRepository
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
        convenio_repo: Optional[ConvenioRepository] = None,
        tutor_emp_repo: Optional[TutorEmpresarialRepository] = None,
    ) -> None:
        self.oferta_service = oferta_service or OfertaService()
        self.postulacion_service = postulacion_service or PostulacionService()
        self.practica_service = practica_service or PracticaService()
        self.convenio_repo = convenio_repo or ConvenioRepository()
        self.tutor_emp_repo = tutor_emp_repo or TutorEmpresarialRepository()

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
        return [x for x in self.postulacion_service.listar_por_id_terna(id_terna) if x.estado_de_postulacion == EstadoPostulacion.VALIDADA]

    def seleccionar_candidato_ganador(
        self, id_pos_aceptada: int, id_p_tutor_emp: int, fecha_inicio: str, fecha_fin: str
    ) -> bool:
        practica = self.practica_service.formalizar_practica(
            id_pos_aceptada, id_p_tutor_emp, fecha_inicio, fecha_fin
        )
        return practica is not None

    def listar_mis_ofertas_publicadas(self, id_e: int) -> list[Oferta]:
        ofertas = self.oferta_service.listar_todas_las_ofertas()
        return [o for o in ofertas if o.id_e == id_e]

    def crear_convenio_empresa(
        self, id_e: int, fecha_firma: str, fecha_vencimiento: str
    ) -> Optional[Convenio]:
        convenio = Convenio(
            id_con=0,
            id_e=id_e,
            fecha_firma=fecha_firma,
            fecha_vencimiento=fecha_vencimiento,
            estado_del_convenio=EstadoConvenio.VIGENTE,
        )
        if self.convenio_repo.guardar(convenio):
            return convenio
        return None

    def obtener_convenios_empresa(self, id_e: int) -> list[Convenio]:
        self.convenio_repo._cargar_datos()
        return [c for c in self.convenio_repo._datos if c.id_e == id_e]

    def obtener_tutores_de_empresa(self, id_e: int) -> list[TutorEmpresarial]:
        return self.tutor_emp_repo.listar_por_empresa(id_e)

    def _obtener_used_oferta_ids(self) -> set[int]:
        self.practica_service.practica_repo._cargar_datos()
        self.practica_service.postulacion_repo._cargar_datos()
        practicas = self.practica_service.practica_repo._datos
        # Build mapping of post_id to offer_id
        post_to_offer = {
            p.id_pos: p.id_o for p in self.practica_service.postulacion_repo._datos
        }
        return {
            post_to_offer[pr.id_pos] for pr in practicas
            if pr.id_pos in post_to_offer
        }

    def obtener_ofertas_activas_empresa(self, id_e: int) -> list[Oferta]:
        used_ids = self._obtener_used_oferta_ids()
        ofertas = self.listar_mis_ofertas_publicadas(id_e)
        return [o for o in ofertas if o.id_o not in used_ids]

    def obtener_historial_ofertas_empresa(self, id_e: int) -> list[Oferta]:
        used_ids = self._obtener_used_oferta_ids()
        ofertas = self.listar_mis_ofertas_publicadas(id_e)
        return [o for o in ofertas if o.id_o in used_ids]

    def _obtener_practicas_por_empresa_y_estados(
        self, id_e: int, estados: set[EstadoPractica]
    ) -> list[Practica]:
        self.practica_service.practica_repo._cargar_datos()
        self.practica_service.postulacion_repo._cargar_datos()
        # Find postulation IDs for this company
        company_post_ids = {
            p.id_pos for p in self.practica_service.postulacion_repo._datos
            if p.id_e == id_e
        }
        return [
            pr for pr in self.practica_service.practica_repo._datos
            if pr.id_pos in company_post_ids and pr.estado_de_practica in estados
        ]

    def obtener_practicas_activas_empresa(self, id_e: int) -> list[Practica]:
        return self._obtener_practicas_por_empresa_y_estados(
            id_e, {EstadoPractica.INICIADA, EstadoPractica.EN_EVALUACION}
        )

    def obtener_historial_practicas_empresa(self, id_e: int) -> list[Practica]:
        return self._obtener_practicas_por_empresa_y_estados(
            id_e, {EstadoPractica.FINALIZADA, EstadoPractica.APROBADA}
        )
