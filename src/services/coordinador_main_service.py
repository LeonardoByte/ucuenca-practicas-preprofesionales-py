from typing import Optional
from src.models import Postulacion
from src.repositories import (
    PracticaRepository,
    FormularioRepository,
    CartaCompromisoRepository,
    PostulacionRepository,
)
from src.services.postulacion_service import PostulacionService
from src.services.interfaces.coordinador_main_service_abc import CoordinadorMainServiceABC


class CoordinadorMainService(CoordinadorMainServiceABC):
    def __init__(
        self,
        postulacion_repo: Optional[PostulacionRepository] = None,
        practica_repo: Optional[PracticaRepository] = None,
        formulario_repo: Optional[FormularioRepository] = None,
        carta_repo: Optional[CartaCompromisoRepository] = None,
        postulacion_service: Optional[PostulacionService] = None,
    ) -> None:
        self.postulacion_repo = postulacion_repo or PostulacionRepository()
        self.practica_repo = practica_repo or PracticaRepository()
        self.formulario_repo = formulario_repo or FormularioRepository()
        self.carta_repo = carta_repo or CartaCompromisoRepository()
        self.postulacion_service = postulacion_service or PostulacionService()

    def revisar_postulaciones_pendientes(self) -> list[Postulacion]:
        self.postulacion_repo._cargar_datos()
        return [p for p in self.postulacion_repo._datos if p.estado_de_postulacion == "Pendiente"]

    def validar_requisitos_alumno(self, id_pos: int, aprobado: bool) -> bool:
        return self.postulacion_service.cambiar_estado(
            id_pos, "Validada" if aprobado else "Rechazada"
        )

    def enviar_terna_a_empresa(self, id_postulaciones: list[int]) -> bool:
        return self.postulacion_service.agrupar_y_despachar_terna(id_postulaciones)

    def ejecutar_cierre_oficial_practica(self, id_pr: int) -> bool:
        practica = self.practica_repo.buscar_por_id(id_pr)
        if not practica:
            return False

        # 1. Obtener y verificar los formularios (1, 2, 3)
        formularios = self.formulario_repo.listar_formularios_por_practica(id_pr)
        tipos_encontrados = {f.tipo_formulario: f.estado_de_firma for f in formularios}

        for f_tipo in ["Formulario 1", "Formulario 2", "Formulario 3"]:
            if f_tipo not in tipos_encontrados:
                return False
            if tipos_encontrados[f_tipo] not in ["Completado", "Aprobado"]:
                return False

        # 2. Obtener y verificar la Carta de Compromiso
        carta = self.carta_repo.buscar_por_practica(id_pr)
        if not carta or carta.estado != "Firmada":
            return False

        # Cierre exitoso, cambiar estado de la práctica
        practica.estado_de_practica = "Aprobada"
        return self.practica_repo.guardar(practica)
