from typing import Optional

from src.models import EstadoPostulacion, Postulacion
from src.repositories import PostulacionRepository
from src.services.exceptions import TernaInvalidaError
from src.services.interfaces.postulacion_service_abc import PostulacionServiceABC


class PostulacionService(PostulacionServiceABC):
    def __init__(self, postulacion_repo: Optional[PostulacionRepository] = None) -> None:
        self.postulacion_repo = postulacion_repo or PostulacionRepository()

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
        if self.postulacion_repo.guardar(post):
            return post
        return None

    def cambiar_estado(self, id_pos: int, nuevo_estado: EstadoPostulacion) -> bool:
        post = self.postulacion_repo.buscar_por_id(id_pos)
        if not post:
            return False
        post.estado_de_postulacion = nuevo_estado
        return self.postulacion_repo.guardar(post)

    def buscar_postulacion_por_id(self, id_pos: int) -> Optional[Postulacion]:
        return self.postulacion_repo.buscar_por_id(id_pos)

    def _actualizar_y_guardar_terna(self, p: Postulacion, next_terna_id: int) -> bool:
        p.id_terna = next_terna_id
        return self.postulacion_repo.guardar(p)

    def agrupar_y_despachar_terna(self, id_postulaciones: list[int]) -> bool:
        if not id_postulaciones:
            raise TernaInvalidaError(
                "Debe seleccionar al menos una postulación para despachar."
            )

        # Cargar postulaciones usando list comprehension sin bucle for
        postulaciones = [self.postulacion_repo.buscar_por_id(id_pos) for id_pos in id_postulaciones]

        # Verificar si alguna postulación no existe
        if any(p is None for p in postulaciones):
            raise TernaInvalidaError("Una o más postulaciones de la terna no existen.")

        # Verificar homogeneidad: misma oferta y empresa
        same_offer = len({p.id_o for p in postulaciones}) == 1
        same_company = len({p.id_e for p in postulaciones}) == 1
        if not same_offer or not same_company:
            raise TernaInvalidaError(
                "Todas las postulaciones de la terna deben ser para la misma oferta y empresa."
            )

        # Obtener un id_terna único autoincremental
        self.postulacion_repo._cargar_datos()
        ternas = [p.id_terna for p in self.postulacion_repo._datos if p.id_terna is not None]
        next_terna_id = max(ternas) + 1 if ternas else 1

        # Ejecutar mutaciones y guardar de forma funcional
        [self._actualizar_y_guardar_terna(p, next_terna_id) for p in postulaciones]

        return True

    def listar_por_id_terna(self, id_terna: int) -> list[Postulacion]:
        return self.postulacion_repo.listar_por_id_terna(id_terna)
