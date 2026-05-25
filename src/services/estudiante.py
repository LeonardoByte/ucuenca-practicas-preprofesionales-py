from datetime import date

from src.models import Oferta, SolicitudAutorizacion, SolicitudOficio
from src.repositories.interfaces.estudiante import EstudianteRepositoryABC
from src.repositories.interfaces.oferta import OfertaRepositoryABC
from src.repositories.interfaces.solicitud_autorizacion import (
    SolicitudAutorizacionRepositoryABC,
)
from src.repositories.interfaces.solicitud_oficio import (
    SolicitudOficioRepositoryABC,
)
from src.services.interfaces.estudiante import EstudianteServiceABC


class EstudianteService(EstudianteServiceABC):
    def __init__(
        self,
        estudiante_repo: EstudianteRepositoryABC,
        oferta_repo: OfertaRepositoryABC,
        solicitud_autorizacion_repo: SolicitudAutorizacionRepositoryABC,
        solicitud_oficio_repo: SolicitudOficioRepositoryABC,
    ) -> None:
        self.estudiante_repo = estudiante_repo
        self.oferta_repo = oferta_repo
        self.solicitud_autorizacion_repo = solicitud_autorizacion_repo
        self.solicitud_oficio_repo = solicitud_oficio_repo

    def verificar_elegibilidad(self, id_p_estudiante: int) -> bool:
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

        return is_matriculado and ciclo >= 6 and has_no_prior_practicas and has_no_active_practicas

    def obtener_ofertas_priorizadas(self, id_p_estudiante: int) -> list[Oferta]:
        ofertas_abiertas = list(
            filter(
                lambda o: o.descripcion_oferta != "",
                self.oferta_repo.listar_ofertas_disponibles(),
            )
        )

        estudiante = self.estudiante_repo.buscar_por_id(id_p_estudiante)
        if (
            estudiante
            and int(estudiante.ciclo_actual) >= 6
            and estudiante.estado_practica == "Sin Practicas"
        ):
            return sorted(
                ofertas_abiertas,
                key=lambda o: estudiante.ciclo_actual in o.requisitos,
                reverse=True,
            )
        return ofertas_abiertas

    def registrar_solicitud_autorizacion(
        self, id_p_estudiante: int, nombre_empresa: str, detalles_empresa: str
    ) -> SolicitudAutorizacion:
        sol = SolicitudAutorizacion(
            id_sol_aut=0,
            id_p_estudiante=id_p_estudiante,
            nombre_empresa=nombre_empresa,
            detalles_empresa=detalles_empresa,
            fecha_solicitud=date.today().strftime("%Y-%m-%d"),
            estado_solicitud="Pendiente",
        )
        self.solicitud_autorizacion_repo.guardar(sol)
        return sol

    def registrar_solicitud_oficio(
        self,
        id_p_estudiante: int,
        nombre_destinatario: str,
        cargo_destinatario: str,
        nombre_empresa: str,
    ) -> SolicitudOficio:
        sol = SolicitudOficio(
            id_sol_of=0,
            id_p_estudiante=id_p_estudiante,
            nombre_destinatario=nombre_destinatario,
            cargo_destinatario=cargo_destinatario,
            nombre_empresa=nombre_empresa,
            fecha_solicitud=date.today().strftime("%Y-%m-%d"),
            estado_solicitud="Pendiente",
        )
        self.solicitud_oficio_repo.guardar(sol)
        return sol
