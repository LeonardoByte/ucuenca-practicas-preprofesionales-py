from abc import ABC, abstractmethod

from src.models import EstadoFirmaFormulario


class TutorEmpresarialMainServiceABC(ABC):
    @abstractmethod
    def registrar_evaluacion_formulario3(
        self, id_pr: int, estado_de_firma: EstadoFirmaFormulario, fecha_de_entrega_registro: str
    ) -> bool:
        """
        Delega en PracticaService el registro o actualización del
        Formulario 3 de desempeño en la empresa.
        """
        pass
