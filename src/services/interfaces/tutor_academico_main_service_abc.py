from abc import ABC, abstractmethod

from src.models import (
    Actividad,
    EstadoFirmaFormulario,
    EstadoValidacionActividad,
    Practica,
)


class TutorAcademicoMainServiceABC(ABC):
    @abstractmethod
    def evaluar_actividad_alumno(
        self, id_act: int, id_pr: int, estado: EstadoValidacionActividad
    ) -> bool:
        """
        Delega en PracticaService el cambio de estado de validación
        de la tarea ('Validada'/'Rechazada').
        """
        pass

    @abstractmethod
    def registrar_evaluacion_formulario2(
        self, id_pr: int, estado_de_firma: EstadoFirmaFormulario, fecha_de_entrega_registro: str
    ) -> bool:
        """Delega en PracticaService el registro o actualización del Formulario 2 académico."""
        pass

    @abstractmethod
    def obtener_practicas_tutor_acad(self, id_p_tutor_acad: int) -> list[Practica]:
        """
        Filtra funcionalmente las prácticas asignadas a este docente.
        """
        pass

    @abstractmethod
    def listar_actividades_de_practica(self, id_pr: int) -> list[Actividad]:
        """
        Recupera todas las actividades registradas en la bitácora de una práctica.
        """
        pass
