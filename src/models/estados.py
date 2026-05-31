from enum import Enum


class EstadoMatricula(str, Enum):
    MATRICULADO = "Matriculado"
    NO_MATRICULADO = "No Matriculado"


class EstadoPracticaEstudiante(str, Enum):
    SIN_PRACTICAS = "Sin Practicas"
    ACTIVA = "Activa"
    FINALIZADA = "Finalizada"


class EstadoConvenio(str, Enum):
    VIGENTE = "Vigente"
    NO_VIGENTE = "No Vigente"


class TipoFormulario(str, Enum):
    FORMULARIO_1 = "Formulario 1"
    FORMULARIO_2 = "Formulario 2"
    FORMULARIO_3 = "Formulario 3"


class EstadoPostulacion(str, Enum):
    PENDIENTE = "Pendiente"
    VALIDADA = "Validada" # Cuando el coordinador valida
    ACEPTADA = "Aceptada" # Cuando la empresa acepta
    RECHAZADA = "Rechazada" # Cuando el coordinador o la empresa rechaza


class EstadoPractica(str, Enum):
    INICIADA = "Iniciada"
    EN_EVALUACION = "En Evaluacion"
    FINALIZADA = "Finalizada"
    APROBADA = "Aprobada"


class EstadoValidacionActividad(str, Enum):
    PROPUESTA = "Propuesta"
    VALIDADA = "Validada"
    RECHAZADA = "Rechazada"


class EstadoFirmaFormulario(str, Enum):
    PRESENTADO = "Presentado"
    COMPLETADO = "Completado"
    APROBADO = "Aprobado"


class EstadoSolicitudAutorizacion(str, Enum):
    PENDIENTE = "Pendiente"
    APROBADA = "Aprobada"
    RECHAZADA = "Rechazada"


class EstadoSolicitudOficio(str, Enum):
    PENDIENTE = "Pendiente"
    EMITIDA = "Emitida"
    RECHAZADA = "Rechazada"


class EstadoCartaCompromiso(str, Enum):
    PENDIENTE = "Pendiente"
    ENTREGADA = "Entregada"
    FIRMADA = "Firmada"


class RolPersona(str, Enum):
    ESTUDIANTE = "Estudiante"
    PERSONAL = "Personal"


class RolPersonal(str, Enum):
    ADMINISTRADOR = "Administrador"
    TUTOR_ACADEMICO = "Tutor Academico"
    TUTOR_EMPRESARIAL = "Tutor Empresarial"
    COORDINADOR = "Coordinador"


class RolUsuario(str, Enum):
    ESTUDIANTE = "Estudiante"
    COORDINADOR = "Coordinador"
    TUTOR_ACADEMICO = "Tutor Academico"
    TUTOR_EMPRESARIAL = "Tutor Empresarial"
    ADMINISTRADOR = "Administrador"
    EMPRESARIO = "Empresa"
