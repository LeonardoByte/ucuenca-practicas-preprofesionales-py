from src.models.empresa import Convenio, Empresa, Oferta
from src.models.persona import (
    CoordinadorDePracticas,
    Estudiante,
    Persona,
    Personal,
    TutorAcademico,
    TutorEmpresarial,
)
from src.models.practica import Actividad, Formulario, Postulacion, Practica
from src.models.solicitud import CartaCompromiso, SolicitudAutorizacion, SolicitudOficio

__all__ = [
    "Persona",
    "Estudiante",
    "Personal",
    "CoordinadorDePracticas",
    "TutorAcademico",
    "TutorEmpresarial",
    "Empresa",
    "Convenio",
    "Oferta",
    "SolicitudAutorizacion",
    "SolicitudOficio",
    "CartaCompromiso",
    "Postulacion",
    "Practica",
    "Actividad",
    "Formulario",
]
