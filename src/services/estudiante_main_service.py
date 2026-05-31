from typing import Optional

from src.models import (
    Actividad,
    EstadoMatricula,
    EstadoPractica,
    EstadoPracticaEstudiante,
    EstadoSolicitudAutorizacion,
    EstadoSolicitudOficio,
    Oferta,
    Postulacion,
    Practica,
    SolicitudAutorizacion,
    SolicitudOficio,
)
from src.repositories import (
    EstudianteRepository,
    SolicitudAutorizacionRepository,
    SolicitudOficioRepository,
)
from src.services.exceptions import (
    CicloNoPermitidoError,
    EstudianteConPracticaActivaError,
    RequisitosNoCumplidosError,
)
from src.services.interfaces.estudiante_main_service_abc import EstudianteMainServiceABC
from src.services.oferta_service import OfertaService
from src.services.postulacion_service import PostulacionService
from src.services.practica_service import PracticaService


class EstudianteMainService(EstudianteMainServiceABC):
    def __init__(
        self,
        estudiante_repo: Optional[EstudianteRepository] = None,
        sol_aut_repo: Optional[SolicitudAutorizacionRepository] = None,
        sol_of_repo: Optional[SolicitudOficioRepository] = None,
        oferta_service: Optional[OfertaService] = None,
        postulacion_service: Optional[PostulacionService] = None,
        practica_service: Optional[PracticaService] = None,
    ) -> None:
        self.estudiante_repo = estudiante_repo or EstudianteRepository()
        self.sol_aut_repo = sol_aut_repo or SolicitudAutorizacionRepository()
        self.sol_of_repo = sol_of_repo or SolicitudOficioRepository()
        self.oferta_service = oferta_service or OfertaService()
        self.postulacion_service = postulacion_service or PostulacionService()
        self.practica_service = practica_service or PracticaService()

    def obtener_catalogo_ofertas(self, id_p_estudiante: int) -> list[Oferta]:
        est = self.estudiante_repo.buscar_por_id(id_p_estudiante)
        if not est:
            return []

        if est.ciclo_actual < 6:
            raise CicloNoPermitidoError(
                "El estudiante no cumple con el ciclo mínimo requerido (>= 6)."
            )

        ofertas = self.oferta_service.listar_todas_las_ofertas()

        # El estudiante no tiene experiencia si estado_practica no es FINALIZADA
        has_no_experience = est.estado_practica != EstadoPracticaEstudiante.FINALIZADA

        if has_no_experience:
            # Prioridad: remuneración DESC
            return sorted(ofertas, key=lambda x: -x.remuneracion)
        else:
            # Por defecto: remuneración ASC
            return sorted(ofertas, key=lambda x: x.remuneracion)

    def solicitar_postulacion(
        self, id_p_estudiante: int, id_o: int, id_e: int, fecha_postulacion: str
    ) -> Optional[Postulacion]:
        est = self.estudiante_repo.buscar_por_id(id_p_estudiante)
        if not est:
            return None

        # Requisitos: ciclo >= 6 y matriculado
        if est.ciclo_actual < 6 or est.estado_de_matricula != EstadoMatricula.MATRICULADO:
            raise RequisitosNoCumplidosError(
                "El estudiante no cumple los requisitos académicos (matrícula o ciclo)."
            )

        # Requisitos: no práctica activa
        if est.estado_practica == EstadoPracticaEstudiante.ACTIVA:
            raise EstudianteConPracticaActivaError(
                "El estudiante ya posee una práctica activa."
            )

        return self.postulacion_service.registrar_postulacion(
            id_p_estudiante, id_o, id_e, None, fecha_postulacion
        )

    def registrar_solicitud_oficio(
        self,
        id_p_estudiante: int,
        nombre_destinatario: str,
        cargo_destinatario: str,
        nombre_empresa: str,
        fecha_solicitud: str,
    ) -> Optional[SolicitudOficio]:
        sol = SolicitudOficio(
            id_sol_of=0,
            id_p_estudiante=id_p_estudiante,
            nombre_destinatario=nombre_destinatario,
            cargo_destinatario=cargo_destinatario,
            nombre_empresa=nombre_empresa,
            fecha_solicitud=fecha_solicitud,
            estado_solicitud=EstadoSolicitudOficio.PENDIENTE,
        )
        if self.sol_of_repo.guardar(sol):
            return sol
        return None

    def registrar_solicitud_autorizacion(
        self, id_p_estudiante: int, nombre_empresa: str, detalles_empresa: str, fecha_solicitud: str
    ) -> Optional[SolicitudAutorizacion]:
        sol = SolicitudAutorizacion(
            id_sol_aut=0,
            id_p_estudiante=id_p_estudiante,
            nombre_empresa=nombre_empresa,
            detalles_empresa=detalles_empresa,
            fecha_solicitud=fecha_solicitud,
            estado_solicitud=EstadoSolicitudAutorizacion.PENDIENTE,
        )
        if self.sol_aut_repo.guardar(sol):
            return sol
        return None

    def obtener_mis_solicitudes_autorizacion(
        self, id_p_estudiante: int
    ) -> list[SolicitudAutorizacion]:
        return self.sol_aut_repo.listar_por_estudiante(id_p_estudiante)

    def obtener_mis_solicitudes_oficio(
        self, id_p_estudiante: int
    ) -> list[SolicitudOficio]:
        return self.sol_of_repo.listar_por_estudiante(id_p_estudiante)

    def registrar_actividad_bitacora(
        self, id_pr: int, descripcion_de_la_tarea: str
    ) -> Optional[Actividad]:
        return self.practica_service.registrar_actividad(id_pr, descripcion_de_la_tarea)

    def obtener_practica_activa_estudiante(self, id_p_estudiante: int) -> Optional[Practica]:
        self.postulacion_service.postulacion_repo._cargar_datos()
        self.practica_service.practica_repo._cargar_datos()

        student_post_ids = {
            p.id_pos for p in self.postulacion_service.postulacion_repo._datos
            if p.id_p_estudiante == id_p_estudiante
        }

        matching_practices = [
            pr for pr in self.practica_service.practica_repo._datos
            if pr.id_pos in student_post_ids
            and pr.estado_de_practica in {EstadoPractica.INICIADA, EstadoPractica.EN_EVALUACION}
        ]
        return matching_practices[0] if matching_practices else None

    def obtener_mis_postulaciones(self, id_p_estudiante: int) -> list[Postulacion]:
        self.postulacion_service.postulacion_repo._cargar_datos()
        return [
            p for p in self.postulacion_service.postulacion_repo._datos
            if p.id_p_estudiante == id_p_estudiante
        ]


