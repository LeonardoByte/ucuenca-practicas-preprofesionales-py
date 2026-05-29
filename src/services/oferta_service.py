from typing import Optional

from src.models import Oferta
from src.repositories import OfertaRepository
from src.services.interfaces.oferta_service_abc import OfertaServiceABC


class OfertaService(OfertaServiceABC):
    def __init__(self, repo: Optional[OfertaRepository] = None) -> None:
        self.repo = repo or OfertaRepository()

    def crear_oferta(
        self,
        id_e: int,
        descripcion: str,
        requisitos: str,
        fecha_de_publicacion: str,
        duracion: str,
        remuneracion: float
    ) -> Optional[Oferta]:
        oferta = Oferta(
            id_o=0,
            id_e=id_e,
            descripcion_oferta=descripcion,
            requisitos=requisitos,
            fecha_de_publicacion=fecha_de_publicacion,
            duracion=duracion,
            remuneracion=remuneracion
        )
        if self.repo.guardar(oferta):
            return oferta
        return None

    def buscar_oferta_por_id(self, id_o: int) -> Optional[Oferta]:
        return self.repo.buscar_por_id(id_o)

    def listar_todas_las_ofertas(self) -> list[Oferta]:
        return self.repo.listar_todas()
