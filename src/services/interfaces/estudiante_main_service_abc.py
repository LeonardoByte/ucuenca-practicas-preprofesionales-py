from abc import ABC, abstractmethod
from typing import Optional

from src.models import Actividad, Oferta, Postulacion, SolicitudAutorizacion, SolicitudOficio


class EstudianteMainServiceABC(ABC):
    @abstractmethod
    def obtener_catalogo_ofertas(self, id_p_estudiante: int) -> list[Oferta]:
        """
        Usa OfertaService para listar vacantes globales y aplica
        filtros/lambda basados en el ciclo.
        """
        pass

    @abstractmethod
    def solicitar_postulacion(
        self, id_p_estudiante: int, id_o: int, id_e: int, fecha_postulacion: str
    ) -> Optional[Postulacion]:
        """Delega en PostulacionService. Si falla la persistencia binaria, retorna None."""
        pass

    @abstractmethod
    def registrar_solicitud_oficio(
        self,
        id_p_estudiante: int,
        nombre_destinatario: str,
        cargo_destinatario: str,
        nombre_empresa: str,
        fecha_solicitud: str,
    ) -> Optional[SolicitudOficio]:
        """Crea un trámite de oficio formal. Retorna None si falla el almacenamiento binario."""
        pass

    @abstractmethod
    def registrar_solicitud_autorizacion(
        self, id_p_estudiante: int, nombre_empresa: str, detalles_empresa: str, fecha_solicitud: str
    ) -> Optional[SolicitudAutorizacion]:
        """
        Crea un trámite de empresa propia. Retorna None si el
        repositorio rechaza la escritura.
        """
        pass

    @abstractmethod
    def obtener_mis_solicitudes_autorizacion(
        self, id_p_estudiante: int
    ) -> list[SolicitudAutorizacion]:
        """
        Retorna historial de autorizaciones según el ID del estudiante.
        """
        pass

    @abstractmethod
    def obtener_mis_solicitudes_oficio(
        self, id_p_estudiante: int
    ) -> list[SolicitudOficio]:
        """
        Retorna historial de oficios emitidos según el ID del estudiante.
        """
        pass

    @abstractmethod
    def registrar_actividad_bitacora(
        self, id_pr: int, descripcion_de_la_tarea: str
    ) -> Optional[Actividad]:
        """Delega en PracticaService la inserción de una nueva tarea en la bitácora del alumno."""
        pass
