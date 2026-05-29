from abc import ABC, abstractmethod

from src.models import Postulacion


class CoordinadorMainServiceABC(ABC):

    @abstractmethod
    def revisar_postulaciones_pendientes(self) -> list[Postulacion]:
        """Consulta en PostulacionService los registros cuyo estado es 'Pendiente'."""
        pass

    @abstractmethod
    def validar_requisitos_alumno(self, id_pos: int, aprobado: bool) -> bool:
        """Modifica el estado a 'Validada' o 'Rechazada' usando PostulacionService. Devuelve False si no se guardó."""
        pass

    @abstractmethod
    def enviar_terna_a_empresa(self, id_postulaciones: list[int]) -> bool:
        """Invoca a PostulacionService para estampar un id_terna único al bloque de candidatos validados."""
        pass

    @abstractmethod
    def ejecutar_cierre_oficial_practica(self, id_pr: int) -> bool:
        """Aduana Zero-Trust: Verifica que los formularios 2 y 3 estén 'Completado' y la Carta Compromiso 'Firmada'."""
        pass
