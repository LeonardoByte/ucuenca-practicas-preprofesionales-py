from typing import Optional
from src.models import (
    Oferta,
    Postulacion,
    SolicitudAutorizacion,
    SolicitudOficio,
    Actividad,
)
from src.repositories import (
    EstudianteRepository,
    SolicitudAutorizacionRepository,
    SolicitudOficioRepository,
)
from src.services.oferta_service import OfertaService
from src.services.postulacion_service import PostulacionService
from src.services.practica_service import PracticaService
from src.services.interfaces.estudiante_main_service_abc import EstudianteMainServiceABC
from src.services.exceptions import CicloNoPermitidoError, EstudianteConPracticaActivaError


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

        # Regla: ciclo_actual >= 6 para ver o aplicar a ofertas
        if est.ciclo_actual < 6:
            raise CicloNoPermitidoError("El estudiante no cumple con el ciclo mínimo requerido (>= 6).")

        return self.oferta_service.listar_todas_las_ofertas()

    def solicitar_postulacion(
        self,
        id_p_estudiante: int,
        id_o: int,
        id_e: int,
        id_p_coordinador: int,
        fecha_postulacion: str
    ) -> Optional[Postulacion]:
        est = self.estudiante_repo.buscar_por_id(id_p_estudiante)
        if not est:
            return None

        # Regla: ciclo_actual >= 6
        if est.ciclo_actual < 6:
            raise CicloNoPermitidoError("El estudiante no cumple con el ciclo mínimo requerido (>= 6).")

        # Regla: No poseer práctica activa
        if est.estado_practica == "Activa":
            raise EstudianteConPracticaActivaError("El estudiante ya posee una práctica activa.")

        return self.postulacion_service.registrar_postulacion(
            id_p_estudiante, id_o, id_e, id_p_coordinador, fecha_postulacion
        )

    def registrar_solicitud_autorizacion(
        self,
        id_p_estudiante: int,
        nombre_empresa: str,
        detalles_empresa: str,
        fecha_solicitud: str
    ) -> Optional[SolicitudAutorizacion]:
        sol = SolicitudAutorizacion(
            id_sol_aut=0,
            id_p_estudiante=id_p_estudiante,
            nombre_empresa=nombre_empresa,
            detalles_empresa=detalles_empresa,
            fecha_solicitud=fecha_solicitud,
            estado_solicitud="Pendiente"
        )
        if self.sol_aut_repo.guardar(sol):
            return sol
        return None

    def registrar_solicitud_oficio(
        self,
        id_p_estudiante: int,
        nombre_destinatario: str,
        cargo_destinatario: str,
        nombre_empresa: str,
        fecha_solicitud: str
    ) -> Optional[SolicitudOficio]:
        sol = SolicitudOficio(
            id_sol_of=0,
            id_p_estudiante=id_p_estudiante,
            nombre_destinatario=nombre_destinatario,
            cargo_destinatario=cargo_destinatario,
            nombre_empresa=nombre_empresa,
            fecha_solicitud=fecha_solicitud,
            estado_solicitud="Pendiente"
        )
        if self.sol_of_repo.guardar(sol):
            return sol
        return None

    def registrar_actividad_bitacora(self, id_pr: int, descripcion_de_la_tarea: str) -> Optional[Actividad]:
        return self.practica_service.registrar_actividad(id_pr, descripcion_de_la_tarea)
