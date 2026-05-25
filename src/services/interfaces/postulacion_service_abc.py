from abc import ABC, abstractmethod
from typing import Optional
from src.models.practica import Postulacion

class PostulacionServiceABC(ABC):
    
    @abstractmethod
    def registrar_postulacion(self, id_p_estudiante: int, id_o: int, id_e: int, id_p_coordinador: int, fecha_postulacion: str) -> Optional[Postulacion]:
        """Crea una nueva postulación en estado 'Pendiente' para una oferta."""
        pass

    @abstractmethod
    def cambiar_estado(self, id_pos: int, nuevo_estado: str) -> bool:
        """Actualiza el estado transaccional de una postulación específica."""
        pass

    @abstractmethod
    def buscar_postulacion_por_id(self, id_pos: int) -> Optional[Postulacion]:
        """Recupera un registro de postulación por su ID primario."""
        pass

    @abstractmethod
    def agrupar_y_despachar_terna(self, id_postulaciones: list[int]) -> bool:
        """
        Toma una lista de hasta 3 IDs de postulación, genera un id_terna único,
        y actualiza cada postulación vinculándola a ese grupo histórico.
        """
        pass

    @abstractmethod
    def listar_por_id_terna(self, id_terna: int) -> list[Postulacion]:
        """Recupera el grupo inmutable de postulaciones asociadas a un despacho histórico."""
        pass