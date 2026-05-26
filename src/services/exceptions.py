
class DomainException(Exception):
    """Clase base para excepciones del dominio de negocio."""
    pass


class EstudianteConPracticaActivaError(DomainException):
    """El estudiante ya posee una práctica activa o en curso."""
    pass


class CicloNoPermitidoError(DomainException):
    """El estudiante no cumple con el umbral mínimo del ciclo académico."""
    pass


class TernaInvalidaError(DomainException):
    """La terna no cumple con las condiciones (ej. no son exactamente 3 postulaciones válidas para la misma oferta)."""
    pass
