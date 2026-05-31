from abc import ABC, abstractmethod
from typing import Optional

from src.models import (
    Postulacion,
    Practica,
    SolicitudAutorizacion,
    SolicitudOficio,
)


class CoordinadorMainServiceABC(ABC):
    @abstractmethod
    def revisar_postulaciones_pendientes(self) -> list[Postulacion]:
        """Consulta en PostulacionService los registros cuyo estado es 'Pendiente'."""
        pass

    @abstractmethod
    def validar_requisitos_alumno(self, id_pos: int, aprobado: bool) -> bool:
        """
        Modifica el estado a 'Validada' o 'Rechazada' usando PostulacionService.
        Devuelve False si no se guardó.
        """
        pass

    @abstractmethod
    def enviar_terna_a_empresa(self, id_postulaciones: list[int]) -> bool:
        """
        Invoca a PostulacionService para estampar un id_terna único
        al bloque de candidatos validados.
        """
        pass

    @abstractmethod
    def asignar_tutor_a_practica(self, id_pr: int, id_p_tutor_acad: int) -> bool:
        """Asigna un tutor académico a una práctica activa."""
        pass

    @abstractmethod
    def ejecutar_cierre_oficial_practica(self, id_pr: int) -> bool:
        """
        Aduana Zero-Trust: Verifica que los formularios 2 y 3
        estén 'Completado' y la Carta Compromiso 'Firmada'.
        """
        pass

    @abstractmethod
    def listar_solicitudes_autorizacion_pendientes(self) -> list[SolicitudAutorizacion]:
        """Listar las solicitudes globales pendientes de autorización."""
        pass

    @abstractmethod
    def listar_solicitudes_oficio_pendientes(self) -> list[SolicitudOficio]:
        """Listar las solicitudes globales pendientes de oficio."""
        pass

    @abstractmethod
    def listar_ofertas_con_conteo_validadas(self) -> list[dict]:
        """
        Retorna datos de ofertas con conteo de postulaciones en estado VALIDADA.
        """
        pass

    @abstractmethod
    def evaluar_solicitud_autorizacion(
        self,
        id_sol_aut: int,
        aprobado: bool,
        id_p_coordinador: int,
        nombre_destinatario: Optional[str] = None,
        cargo_destinatario: Optional[str] = None,
    ) -> bool:
        """
        Muta el estado de una solicitud de empresa propia. Si se aprueba, genera
        una SolicitudOficio en estado PENDIENTE.
        """
        pass

    @abstractmethod
    def procesar_emision_oficio(
        self, id_sol_of: int, id_p_coordinador: int, ruta_oficio_pdf: str
    ) -> bool:
        """
        Muta el estado de una solicitud de oficio a EMITIDO y vincula firma del coordinador.
        """
        pass

    @abstractmethod
    def listar_practicas_pendientes_de_tutor(self, id_p_coordinador: int) -> list[Practica]:
        """
        Retorna prácticas en estado INICIADA sin tutor académico, cuyas postulaciones origen
        fueron auditadas por este coordinador.
        """
        pass
