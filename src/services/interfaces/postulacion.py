from abc import ABC, abstractmethod

from src.models import Postulacion


class PostulacionServiceABC(ABC):
    @abstractmethod
    def registrar_postulacion(self, id_p_estudiante: int, id_o: str, id_e: int) -> bool:
        """Valida elegibilidad y la inexistencia de prácticas activas
        antes de registrar la postulación.
        """
        pass

    @abstractmethod
    def validar_postulacion(self, id_pos: int, id_p_coordinador: int, es_valida: bool) -> bool:
        """El coordinador aprueba o rechaza los requisitos académicos del postulante."""
        pass

    @abstractmethod
    def enviar_postulaciones_a_empresa(
        self, id_o: str, id_e: int, id_terna: int
    ) -> list[Postulacion]:
        """Agrupa y despacha hasta 3 postulaciones validadas asignándoles un ID de terna."""
        pass
