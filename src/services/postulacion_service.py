from typing import Optional

from src.models import EstadoPostulacion, Postulacion
from src.repositories import PostulacionRepository
from src.services.exceptions import TernaInvalidaError
from src.services.interfaces.postulacion_service_abc import PostulacionServiceABC


class PostulacionService(PostulacionServiceABC):
    def __init__(self, repo: Optional[PostulacionRepository] = None) -> None:
        self.repo = repo or PostulacionRepository()

    def registrar_postulacion(
        self,
        id_p_estudiante: int,
        id_o: int,
        id_e: int,
        id_p_coordinador: Optional[int],
        fecha_postulacion: str,
    ) -> Optional[Postulacion]:
        post = Postulacion(
            id_pos=0,
            id_p_estudiante=id_p_estudiante,
            id_o=id_o,
            id_e=id_e,
            id_p_coordinador=id_p_coordinador,
            fecha_postulacion=fecha_postulacion,
            estado_de_postulacion=EstadoPostulacion.PENDIENTE
        )
        if self.repo.guardar(post):
            return post
        return None

    def cambiar_estado(self, id_pos: int, nuevo_estado: EstadoPostulacion) -> bool:
        post = self.repo.buscar_por_id(id_pos)
        if not post:
            return False
        post.estado_de_postulacion = nuevo_estado
        return self.repo.guardar(post)

    def buscar_postulacion_por_id(self, id_pos: int) -> Optional[Postulacion]:
        return self.repo.buscar_por_id(id_pos)

    def agrupar_y_despachar_terna(self, id_postulaciones: list[int]) -> bool:
        if len(id_postulaciones) != 3:
            raise TernaInvalidaError(
                "Una terna debe estar compuesta por exactamente 3 postulaciones."
            )

        postulaciones = []
        for id_pos in id_postulaciones:
            post = self.repo.buscar_por_id(id_pos)
            if not post:
                raise TernaInvalidaError(f"La postulación con ID {id_pos} no existe.")
            postulaciones.append(post)

        # Verificar homogeneidad: misma oferta y empresa
        first = postulaciones[0]
        for p in postulaciones[1:]:
            if p.id_o != first.id_o or p.id_e != first.id_e:
                raise TernaInvalidaError(
                    "Todas las postulaciones de la terna deben ser para la misma oferta y empresa."
                )

        # Obtener un id_terna único autoincremental
        self.repo._cargar_datos()
        ternas = [p.id_terna for p in self.repo._datos if p.id_terna is not None]
        next_terna_id = max(ternas) + 1 if ternas else 1

        for p in postulaciones:
            p.id_terna = next_terna_id
            self.repo.guardar(p)

        return True

    def listar_por_id_terna(self, id_terna: int) -> list[Postulacion]:
        return self.repo.listar_por_id_terna(id_terna)
