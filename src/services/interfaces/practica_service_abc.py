from abc import ABC, abstractmethod
from typing import Optional

from src.models.practica import Actividad, Formulario, Practica


class PracticaServiceABC(ABC):

    @abstractmethod
    def formalizar_practica(self, id_pos_aceptada: int, id_p_tutor_acad: int, id_p_tutor_emp: int, fecha_inicio: str, fecha_fin: str) -> Optional[Practica]:
        """
        Muta la postulación seleccionada a 'Aceptada'. Invoca a PostulacionService para 
        pasar el resto de las postulaciones del mismo id_terna/oferta a 'Rechazada'.
        Finalmente, da de alta la entidad Practica en el disco.
        """
        pass

    @abstractmethod
    def registrar_actividad(self, id_pr: int, descripcion: str) -> Actividad:
        """Registra una tarea en estado "Propuesta" por el estudiante dentro de su práctica."""
        pass

    @abstractmethod
    def evaluar_actividad(self, id_act: int, id_pr: int, estado: str) -> bool:
        """Modifica el estado de de una actividad "Validada" o "Rechazada"."""
        pass

    @abstractmethod
    def actualizar_formulario(self, id_pr: int, tipo_formulario: str, estado_firma: str, fecha_entrega: str, numero_formulario: str) -> Formulario:
        """Administra el ciclo de vida y control de firmas de las rúbricas 1, 2 y 3."""
        pass

    @abstractmethod
    def registrar_entrega_carta_compromiso(self, id_pr: int, ruta_pdf: str, nuevo_estado: str) -> bool:
        """Muta el control del documento legal ('Pendiente' -> 'Entregada' -> 'Firmada')."""
        pass
