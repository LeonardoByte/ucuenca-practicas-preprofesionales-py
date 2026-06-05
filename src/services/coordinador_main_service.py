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
    Practica,
    SolicitudAutorizacion,
    SolicitudOficio,
    TipoFormulario,
)
from src.repositories import (
    CartaCompromisoRepository,
    EstudianteRepository,
    FormularioRepository,
    OfertaRepository,
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
        oferta_repo: Optional[OfertaRepository] = None,
    ) -> None:
        self.postulacion_repo = postulacion_repo or PostulacionRepository()
        self.practica_repo = practica_repo or PracticaRepository()
        self.formulario_repo = formulario_repo or FormularioRepository()
        self.carta_repo = carta_repo or CartaCompromisoRepository()
        self.estudiante_repo = estudiante_repo or EstudianteRepository()
        self.postulacion_service = postulacion_service or PostulacionService()
        self.sol_aut_repo = sol_aut_repo or SolicitudAutorizacionRepository()
        self.sol_of_repo = sol_of_repo or SolicitudOficioRepository()
        self.oferta_repo = oferta_repo or OfertaRepository()

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

        # Formulario 1 puede estar PRESENTADO, COMPLETADO o APROBADO
        f1_valid = [
            f for f in formularios
            if f.tipo_formulario == TipoFormulario.FORMULARIO_1
            and f.estado_de_firma in {
                EstadoFirmaFormulario.PRESENTADO,
                EstadoFirmaFormulario.COMPLETADO,
                EstadoFirmaFormulario.APROBADO,
            }
        ]
        # Formulario 2 y 3 deben estar COMPLETADO o APROBADO
        f23_valid = [
            f for f in formularios
            if f.tipo_formulario in {TipoFormulario.FORMULARIO_2, TipoFormulario.FORMULARIO_3}
            and f.estado_de_firma in {
                EstadoFirmaFormulario.COMPLETADO,
                EstadoFirmaFormulario.APROBADO,
            }
        ]

        forms_complete = (
            len(f1_valid) >= 1
            and len({f.tipo_formulario for f in f23_valid}) == 2
        )

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

    def listar_ofertas_con_conteo_validadas(self) -> list[dict]:
        self.oferta_repo._cargar_datos()
        self.postulacion_repo._cargar_datos()

        ofertas = self.oferta_repo._datos
        postulaciones = self.postulacion_repo._datos

        return [
            {
                "id_o": o.id_o,
                "id_e": o.id_e,
                "descripcion_oferta": o.descripcion_oferta,
                "requisitos": o.requisitos,
                "fecha_de_publicacion": o.fecha_de_publicacion,
                "duracion": o.duracion,
                "remuneracion": o.remuneracion,
                "conteo_validadas": len([
                    p for p in postulaciones
                    if p.id_o == o.id_o
                    and p.estado_de_postulacion == EstadoPostulacion.VALIDADA
                ])
            }
            for o in ofertas
        ]

    def evaluar_solicitud_autorizacion(
        self,
        id_sol_aut: int,
        aprobado: bool,
        id_p_coordinador: int,
        nombre_destinatario: Optional[str] = None,
        cargo_destinatario: Optional[str] = None,
    ) -> bool:
        sol = self.sol_aut_repo.buscar_por_id(id_sol_aut)
        if not sol:
            return False

        sol.estado_solicitud = (
            EstadoSolicitudAutorizacion.APROBADA if aprobado
            else EstadoSolicitudAutorizacion.RECHAZADA
        )
        sol.id_p_coordinador = id_p_coordinador

        if not self.sol_aut_repo.guardar(sol):
            return False

        if aprobado:
            self.sol_of_repo._cargar_datos()
            current_ids = [s.id_sol_of for s in self.sol_of_repo._datos]
            new_id = max(current_ids) + 1 if current_ids else 1

            oficio = SolicitudOficio(
                id_sol_of=new_id,
                id_p_estudiante=sol.id_p_estudiante,
                nombre_destinatario=nombre_destinatario or "Por definir",
                cargo_destinatario=cargo_destinatario or "Representante Legal",
                nombre_empresa=sol.nombre_empresa,
                fecha_solicitud=sol.fecha_solicitud,
                estado_solicitud=EstadoSolicitudOficio.PENDIENTE,
            )
            oficio.id_p_coordinador = id_p_coordinador
            return self.sol_of_repo.guardar(oficio)

        return True

    def procesar_emision_oficio(
        self, id_sol_of: int, id_p_coordinador: int, ruta_oficio_pdf: str
    ) -> bool:
        sol = self.sol_of_repo.buscar_por_id(id_sol_of)
        if not sol:
            return False

        sol.estado_solicitud = EstadoSolicitudOficio.EMITIDA
        sol.id_p_coordinador = id_p_coordinador
        sol.ruta_oficio_pdf = ruta_oficio_pdf
        return self.sol_of_repo.guardar(sol)

    def listar_practicas_pendientes_de_tutor(self, id_p_coordinador: int) -> list[Practica]:
        self.practica_repo._cargar_datos()
        self.postulacion_repo._cargar_datos()

        valid_post_ids = {
            p.id_pos for p in self.postulacion_repo._datos
            if p.id_p_coordinador == id_p_coordinador
        }

        return [
            pr for pr in self.practica_repo._datos
            if pr.estado_de_practica == EstadoPractica.INICIADA
            and pr.id_p_tutor_acad == 0
            and pr.id_pos in valid_post_ids
        ]
