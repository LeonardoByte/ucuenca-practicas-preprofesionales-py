class DomainError(Exception):
    """Clase base para excepciones del dominio de negocio."""
    pass


class EstudianteConPracticaActivaError(DomainError):
    """El estudiante ya posee una práctica activa o en curso."""
    pass


class CicloNoPermitidoError(DomainError):
    """El estudiante no cumple con el umbral mínimo del ciclo académico."""
    pass


class TernaInvalidaError(DomainError):
    """La terna no cumple con las condiciones de homogeneidad o tamaño."""
    pass


class CredencialesInvalidasError(DomainError):
    """El usuario no existe o la contraseña ingresada es incorrecta."""
    pass


class CorreoDuplicadoError(DomainError):
    """El correo electrónico ya se encuentra registrado en el sistema."""
    pass


class RequisitosNoCumplidosError(DomainError):
    """El estudiante no cumple los requisitos académicos (matrícula o ciclo)."""
    pass


class DocumentacionIncompletaError(DomainError):
    """Faltan firmas o formularios obligatorios para completar la práctica."""
    pass


class EvaluacionTempranaError(DomainError):
    """La evaluación final se registra antes del plazo permitido (7 días)."""
    pass

