from typing import Optional

from src.models import (
    EstadoCartaCompromiso,
    EstadoFirmaFormulario,
    EstadoPostulacion,
    EstadoPractica,
    EstadoPracticaEstudiante,
    EstadoSolicitudAutorizacion,
    EstadoSolicitudOficio,
    Postulacion,
    SolicitudAutorizacion,
    SolicitudOficio,
    TipoFormulario,
)
from src.repositories import (
    CartaCompromisoRepository,
    EstudianteRepository,
    FormularioRepository,
    PostulacionRepository,
    PracticaRepository,
    SolicitudAutorizacionRepository,
    SolicitudOficioRepository,
)
from src.services.exceptions import DocumentacionIncompletaError
from src.services.interfaces.coordinador_main_service_abc import CoordinadorMainServiceABC
from src.services.postulacion_service import PostulacionService


class CoordinadorMainService(CoordinadorMainServiceABC):
    def __init__(
        self,
        postulacion_repo: Optional[PostulacionRepository] = None,
        practica_repo: Optional[PracticaRepository] = None,
        formulario_repo: Optional[FormularioRepository] = None,
        carta_repo: Optional[CartaCompromisoRepository] = None,
        estudiante_repo: Optional[EstudianteRepository] = None,
        postulacion_service: Optional[PostulacionService] = None,
        sol_aut_repo: Optional[SolicitudAutorizacionRepository] = None,
        sol_of_repo: Optional[SolicitudOficioRepository] = None,
    ) -> None:
        self.postulacion_repo = postulacion_repo or PostulacionRepository()
        self.practica_repo = practica_repo or PracticaRepository()
        self.formulario_repo = formulario_repo or FormularioRepository()
        self.carta_repo = carta_repo or CartaCompromisoRepository()
        self.estudiante_repo = estudiante_repo or EstudianteRepository()
        self.postulacion_service = postulacion_service or PostulacionService()
        self.sol_aut_repo = sol_aut_repo or SolicitudAutorizacionRepository()
        self.sol_of_repo = sol_of_repo or SolicitudOficioRepository()

    def revisar_postulaciones_pendientes(self) -> list[Postulacion]:
        self.postulacion_repo._cargar_datos()
        # Filtrado funcional sin bucle for
        return [
            p for p in self.postulacion_repo._datos
            if p.estado_de_postulacion == EstadoPostulacion.PENDIENTE
        ]

    def validar_requisitos_alumno(self, id_pos: int, aprobado: bool) -> bool:
        nuevo_estado = (
            EstadoPostulacion.VALIDADA
            if aprobado
            else EstadoPostulacion.RECHAZADA
        )
        return self.postulacion_service.cambiar_estado(id_pos, nuevo_estado)

    def enviar_terna_a_empresa(self, id_postulaciones: list[int]) -> bool:
        return self.postulacion_service.agrupar_y_despachar_terna(id_postulaciones)

    def asignar_tutor_a_practica(self, id_pr: int, id_p_tutor_acad: int) -> bool:
        practica = self.practica_repo.buscar_por_id(id_pr)
        if not practica:
            return False
        practica.id_p_tutor_acad = id_p_tutor_acad
        return self.practica_repo.guardar(practica)

    def ejecutar_cierre_oficial_practica(self, id_pr: int) -> bool:
        practica = self.practica_repo.buscar_por_id(id_pr)
        if not practica:
            return False

        # 1. Obtener y verificar los formularios (1, 2, 3)
        formularios = self.formulario_repo.listar_formularios_por_practica(id_pr)
        required_types = {
            TipoFormulario.FORMULARIO_1,
            TipoFormulario.FORMULARIO_2,
            TipoFormulario.FORMULARIO_3,
        }
        valid_states = {EstadoFirmaFormulario.COMPLETADO, EstadoFirmaFormulario.APROBADO}

        valid_forms = [
            f for f in formularios
            if f.tipo_formulario in required_types and f.estado_de_firma in valid_states
        ]
        valid_types = {f.tipo_formulario for f in valid_forms}
        forms_complete = (valid_types == required_types)

        # 2. Obtener y verificar la Carta de Compromiso
        carta = self.carta_repo.buscar_por_practica(id_pr)
        carta_complete = (carta is not None and carta.estado == EstadoCartaCompromiso.FIRMADA)

        if not forms_complete or not carta_complete:
            raise DocumentacionIncompletaError(
                "Faltan firmas o formularios obligatorios para completar la práctica."
            )

        # Cierre exitoso, cambiar estado de la práctica
        practica.estado_de_practica = EstadoPractica.APROBADA
        if self.practica_repo.guardar(practica):
            # También actualizar el estado de la práctica en el estudiante
            post = self.postulacion_repo.buscar_por_id(practica.id_pos)
            if post:
                estudiante = self.estudiante_repo.buscar_por_id(post.id_p_estudiante)
                if estudiante:
                    estudiante.estado_practica = EstadoPracticaEstudiante.FINALIZADA
                    self.estudiante_repo.guardar(estudiante)
            return True
        return False

    def listar_solicitudes_autorizacion_pendientes(self) -> list[SolicitudAutorizacion]:
        self.sol_aut_repo._cargar_datos()
        return [
            s for s in self.sol_aut_repo._datos
            if s.estado_solicitud == EstadoSolicitudAutorizacion.PENDIENTE
        ]

    def listar_solicitudes_oficio_pendientes(self) -> list[SolicitudOficio]:
        self.sol_of_repo._cargar_datos()
        return [
            s for s in self.sol_of_repo._datos
            if s.estado_solicitud == EstadoSolicitudOficio.PENDIENTE
        ]

