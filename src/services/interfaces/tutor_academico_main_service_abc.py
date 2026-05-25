from abc import ABC, abstractmethod

from src.models import Actividad


class TutorAcademicoMainServiceABC(ABC):
    
    @abstractmethod
    def evaluar_actividad_alumno(self, id_act: int, id_pr: int, estado: str) -> bool:
        """Delega en PracticaService el cambio de estado de validación de la tarea ('Validada'/'Rechazada')."""
        pass

    @abstractmethod
    def registrar_evaluacion_formulario2(self, id_pr: int, estado_de_firma: str, fecha_de_entrega_registro: str, numero_formulario: str) -> bool:
        """Delega en PracticaService el registro o actualización del Formulario 2 académico."""
        pass