from src.repositories.interfaces.base import RepositoryABC
from src.repositories.interfaces.carta_compromiso import (
    CartaCompromisoRepositoryABC,
)
from src.repositories.interfaces.estudiante import EstudianteRepositoryABC
from src.repositories.interfaces.formulario import FormularioRepositoryABC
from src.repositories.interfaces.oferta import OfertaRepositoryABC
from src.repositories.interfaces.postulacion import PostulacionRepositoryABC
from src.repositories.interfaces.practica import PracticaRepositoryABC
from src.repositories.interfaces.solicitud_autorizacion import (
    SolicitudAutorizacionRepositoryABC,
)
from src.repositories.interfaces.solicitud_oficio import SolicitudOficioRepositoryABC

__all__ = [
    "RepositoryABC",
    "EstudianteRepositoryABC",
    "OfertaRepositoryABC",
    "PostulacionRepositoryABC",
    "PracticaRepositoryABC",
    "FormularioRepositoryABC",
    "SolicitudAutorizacionRepositoryABC",
    "SolicitudOficioRepositoryABC",
    "CartaCompromisoRepositoryABC",
]
