from abc import ABC, abstractmethod
from typing import Optional

from src.models import Actividad, Empresa, EstadoFirmaFormulario, Practica


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

    @abstractmethod
    def obtener_datos_empresa_tutor(self, id_e: int) -> Optional[Empresa]:
        """
        Recupera directamente el modelo de la empresa asociada.
        """
        pass

    @abstractmethod
    def obtener_practicas_tutor_emp(self, id_p_tutor_emp: int) -> list[Practica]:
        """
        Devuelve las prácticas vigentes gestionadas por el tutor empresarial.
        """
        pass

    @abstractmethod
    def proponer_actividad_practica(self, id_pr: int, descripcion: str) -> Optional[Actividad]:
        """
        Instancia una nueva actividad vinculada a la práctica en estado PROPUESTA.
        """
        pass
