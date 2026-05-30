from typing import Optional

from src.models import (
    EstadoPostulacion,
    EstadoPractica,
    EstadoPracticaEstudiante,
    Postulacion,
)
from src.repositories import (
    CartaCompromisoRepository,
    EstudianteRepository,
    FormularioRepository,
    PostulacionRepository,
    PracticaRepository,
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
    ) -> None:
        self.postulacion_repo = postulacion_repo or PostulacionRepository()
        self.practica_repo = practica_repo or PracticaRepository()
        self.formulario_repo = formulario_repo or FormularioRepository()
        self.carta_repo = carta_repo or CartaCompromisoRepository()
        self.estudiante_repo = estudiante_repo or EstudianteRepository()
        self.postulacion_service = postulacion_service or PostulacionService()

    def revisar_postulaciones_pendientes(self) -> list[Postulacion]:
        self.postulacion_repo._cargar_datos()
        pendientes = []
        for p in self.postulacion_repo._datos:
            est_str = (
                p.estado_de_postulacion.value
                if hasattr(p.estado_de_postulacion, "value")
                else p.estado_de_postulacion
            )
            if str(est_str).strip().lower() == "pendiente":
                pendientes.append(p)
        return pendientes

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
        tipos_encontrados = {}
        for f in formularios:
            val_str = (
                f.estado_de_firma.value
                if hasattr(f.estado_de_firma, "value")
                else f.estado_de_firma
            )
            tipo_str = (
                f.tipo_formulario.value
                if hasattr(f.tipo_formulario, "value")
                else f.tipo_formulario
            )
            tipos_encontrados[str(tipo_str)] = str(val_str)

        incompleto = False
        for f_tipo in ["Formulario 1", "Formulario 2", "Formulario 3"]:
            if (
                f_tipo not in tipos_encontrados
                or tipos_encontrados[f_tipo] not in ["Completado", "Aprobado"]
            ):
                incompleto = True
                break

        # 2. Obtener y verificar la Carta de Compromiso
        carta = self.carta_repo.buscar_por_practica(id_pr)
        carta_estado = (
            carta.estado.value
            if carta and hasattr(carta.estado, "value")
            else (carta.estado if carta else None)
        )
        if not carta or str(carta_estado) != "Firmada":
            incompleto = True

        if incompleto:
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
