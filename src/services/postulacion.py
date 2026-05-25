from datetime import date

from src.models import Postulacion
from src.repositories.interfaces.estudiante import EstudianteRepositoryABC
from src.repositories.interfaces.oferta import OfertaRepositoryABC
from src.repositories.interfaces.postulacion import PostulacionRepositoryABC
from src.repositories.interfaces.practica import PracticaRepositoryABC
from src.services.interfaces.postulacion import PostulacionServiceABC


class PostulacionService(PostulacionServiceABC):
    def __init__(
        self,
        postulacion_repo: PostulacionRepositoryABC,
        estudiante_repo: EstudianteRepositoryABC,
        practica_repo: PracticaRepositoryABC,
        oferta_repo: OfertaRepositoryABC,
    ) -> None:
        self.postulacion_repo = postulacion_repo
        self.estudiante_repo = estudiante_repo
        self.practica_repo = practica_repo
        self.oferta_repo = oferta_repo

    def registrar_postulacion(self, id_p_estudiante: int, id_o: str, id_e: int) -> bool:
        estudiante = self.estudiante_repo.buscar_por_id(id_p_estudiante)
        if not estudiante:
            return False

        try:
            ciclo = int(estudiante.ciclo_actual)
        except ValueError:
            ciclo = 0

        is_matriculado = estudiante.estado_de_matricula == "Matriculado"
        has_no_prior_practicas = (
            estudiante.historial_practicas == "Ninguno"
            or not estudiante.historial_practicas
            or estudiante.historial_practicas == ""
        )
        has_no_active_practicas = estudiante.estado_practica == "Sin Practicas"

        active_pr = self.practica_repo.buscar_practica_activa_estudiante(id_p_estudiante)

        if not (
            is_matriculado
            and ciclo >= 6
            and has_no_prior_practicas
            and has_no_active_practicas
            and not active_pr
        ):
            return False

        post = Postulacion(
            id_pos=0,
            id_p_estudiante=id_p_estudiante,
            id_o=id_o,
            id_e=id_e,
            id_p_coordinador=0,
            fecha_postulacion=date.today().strftime("%Y-%m-%d"),
            estado_de_postulacion="Pendiente",
        )
        return self.postulacion_repo.guardar(post)

    def validar_postulacion(self, id_pos: int, id_p_coordinador: int, es_valida: bool) -> bool:
        post = self.postulacion_repo.buscar_por_id(id_pos)
        if not post:
            return False

        post.id_p_coordinador = id_p_coordinador
        post.estado_de_postulacion = "Validada" if es_valida else "Rechazada"
        return self.postulacion_repo.guardar(post)

    def enviar_postulaciones_a_empresa(
        self, id_o: str, id_e: int, id_terna: int
    ) -> list[Postulacion]:
        postulaciones_oferta = self.postulacion_repo.listar_por_oferta_compuesta(id_o, id_e)
        postulaciones_validadas = list(
            filter(
                lambda p: p.estado_de_postulacion == "Validada",
                postulaciones_oferta,
            )
        )
        terna = postulaciones_validadas[:3]
        for p in terna:
            p.id_terna = id_terna
            self.postulacion_repo.guardar(p)
        return terna
