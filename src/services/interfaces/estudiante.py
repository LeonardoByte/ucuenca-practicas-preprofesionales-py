from abc import ABC, abstractmethod

from src.models import Oferta, SolicitudAutorizacion, SolicitudOficio


class EstudianteServiceABC(ABC):
    @abstractmethod
    def verificar_elegibilidad(self, id_p_estudiante: int) -> bool:
        """Valida que esté matriculado en sexto ciclo o superior y carezca de prácticas previas."""
        pass

    @abstractmethod
    def obtener_ofertas_priorizadas(self, id_p_estudiante: int) -> list[Oferta]:
        """Filtrar y priorizar ofertas para alumnos elegibles."""
        pass

    @abstractmethod
    def registrar_solicitud_autorizacion(
        self, id_p_estudiante: int, nombre_empresa: str, detalles_empresa: str
    ) -> SolicitudAutorizacion:
        """Registrar solicitud para realizar prácticas en una empresa propia o auto-gestionada."""
        pass

    @abstractmethod
    def registrar_solicitud_oficio(
        self,
        id_p_estudiante: int,
        nombre_destinatario: str,
        cargo_destinatario: str,
        nombre_empresa: str,
    ) -> SolicitudOficio:
        """Registrar solicitud de oficio/certificado dirigida a la empresa."""
        pass

