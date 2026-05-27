"""Módulo 1: Tests unitarios de modelos del dominio y enums.

Verifica la instanciación correcta y el tipado de atributos basados en Enum
para todas las entidades del dominio de negocio.
"""

from src.models import (
    Actividad,
    Administrador,
    CartaCompromiso,
    Convenio,
    CoordinadorDePracticas,
    Empresa,
    EstadoCartaCompromiso,
    EstadoConvenio,
    EstadoFirmaFormulario,
    EstadoMatricula,
    EstadoPostulacion,
    EstadoPractica,
    EstadoPracticaEstudiante,
    EstadoSolicitudAutorizacion,
    EstadoSolicitudOficio,
    EstadoValidacionActividad,
    Estudiante,
    Formulario,
    Persona,
    Personal,
    Postulacion,
    Practica,
    RolPersona,
    RolPersonal,
    RolUsuario,
    SolicitudAutorizacion,
    SolicitudOficio,
    TipoFormulario,
    TutorAcademico,
    TutorEmpresarial,
    Usuario,
)


def test_persona_and_subclasses_typing():
    """Valida la asignación y tipado de RolPersona y RolPersonal en las clases humanas."""
    # 1. Persona Base
    p = Persona(
        id_p=1,
        nombre_y_apellido="Alex Doe",
        cedula_dni="1234567890",
        correo_electronico="alex@unl.edu.ec",
        direccion="Loja",
        rol=RolPersona.ESTUDIANTE,
    )
    assert p.rol == RolPersona.ESTUDIANTE
    assert isinstance(p.rol, RolPersona)

    # 2. Estudiante
    est = Estudiante(
        id_p=2,
        nombre_y_apellido="Juan Perez",
        cedula_dni="1712345678",
        correo_electronico="juan@unl.edu.ec",
        direccion="Loja Centro",
        ciclo_actual=6,
        estado_de_matricula=EstadoMatricula.MATRICULADO,
        malla_academica="malla.pdf",
        curriculum_vitae="cv.pdf",
        historial_practicas="Ninguno",
        estado_practica=EstadoPracticaEstudiante.SIN_PRACTICAS,
    )
    assert est.rol == RolPersona.ESTUDIANTE
    assert est.estado_de_matricula == EstadoMatricula.MATRICULADO
    assert est.estado_practica == EstadoPracticaEstudiante.SIN_PRACTICAS
    assert isinstance(est.estado_de_matricula, EstadoMatricula)

    # 3. Personal Base
    pers = Personal(
        id_p=3,
        nombre_y_apellido="Docente Uno",
        cedula_dni="1798765432",
        correo_electronico="docente@unl.edu.ec",
        direccion="Loja",
        rol_personal=RolPersonal.TUTOR_ACADEMICO,
    )
    assert pers.rol == RolPersona.PERSONAL
    assert pers.rol_personal == RolPersonal.TUTOR_ACADEMICO

    # 4. Especializaciones de Personal
    coord = CoordinadorDePracticas(
        id_p=4,
        nombre_y_apellido="Ana Nuñez",
        cedula_dni="1798765431",
        correo_electronico="ana@unl.edu.ec",
        direccion="Loja",
    )
    assert coord.rol == RolPersona.PERSONAL
    assert coord.rol_personal == RolPersonal.COORDINADOR

    t_acad = TutorAcademico(
        id_p=5,
        nombre_y_apellido="Carlos Mendoza",
        cedula_dni="1723456789",
        correo_electronico="carlos@unl.edu.ec",
        direccion="Loja",
    )
    assert t_acad.rol_personal == RolPersonal.TUTOR_ACADEMICO

    t_emp = TutorEmpresarial(
        id_p=6,
        nombre_y_apellido="Luis Gomez",
        cedula_dni="1734567890",
        correo_electronico="luis@solutions.com",
        direccion="Quito",
        id_e=10,
    )
    assert t_emp.rol_personal == RolPersonal.TUTOR_EMPRESARIAL
    assert t_emp.id_e == 10

    admin = Administrador(
        id_p=7,
        nombre_y_apellido="Sofia Ramirez",
        cedula_dni="1745678901",
        correo_electronico="sofia@unl.edu.ec",
        direccion="Loja",
    )
    assert admin.rol_personal == RolPersonal.ADMINISTRADOR


def test_usuario_typing():
    """Valida que la clase Usuario reciba y conserve RolUsuario."""
    u = Usuario(
        id_u=1,
        username_correo="sofia@unl.edu.ec",
        contrasena="pass123",
        rol=RolUsuario.ADMINISTRADOR,
        id_p=7,
    )
    assert u.rol == RolUsuario.ADMINISTRADOR
    assert isinstance(u.rol, RolUsuario)


def test_empresa_and_convenio_typing():
    """Valida el tipado de los enums en el ecosistema corporativo."""
    emp = Empresa(
        id_e=10,
        nombre_empresa="Tech Solutions S.A.",
        estado_de_convenio_emp=EstadoConvenio.VIGENTE,
        correo_electronico="info@tech.com",
    )
    assert emp.estado_de_convenio_emp == EstadoConvenio.VIGENTE
    assert isinstance(emp.estado_de_convenio_emp, EstadoConvenio)

    conv = Convenio(
        id_con=1,
        id_e=10,
        fecha_firma="2026-01-01",
        fecha_vencimiento="2027-01-01",
        estado_del_convenio=EstadoConvenio.VIGENTE,
    )
    assert conv.estado_del_convenio == EstadoConvenio.VIGENTE


def test_postulacion_and_practica_typing():
    """Valida los enums en el flujo de postulación, práctica, bitácora y formularios."""
    post = Postulacion(
        id_pos=1,
        id_p_estudiante=2,
        id_o=5,
        id_e=10,
        id_p_coordinador=4,
        fecha_postulacion="2026-05-01",
        estado_de_postulacion=EstadoPostulacion.PENDIENTE,
    )
    assert post.estado_de_postulacion == EstadoPostulacion.PENDIENTE
    assert isinstance(post.estado_de_postulacion, EstadoPostulacion)

    prac = Practica(
        id_pr=1,
        id_pos=1,
        id_p_tutor_acad=5,
        id_p_tutor_emp=6,
        fecha_inicio="2026-05-15",
        fecha_fin="2026-11-15",
        estado_de_practica=EstadoPractica.INICIADA,
    )
    assert prac.estado_de_practica == EstadoPractica.INICIADA
    assert isinstance(prac.estado_de_practica, EstadoPractica)

    act = Actividad(
        id_act=1,
        id_pr=1,
        descripcion_de_la_tarea="Desarrollo de API",
        estado_de_validacion=EstadoValidacionActividad.PROPUESTA,
    )
    assert act.estado_de_validacion == EstadoValidacionActividad.PROPUESTA
    assert isinstance(act.estado_de_validacion, EstadoValidacionActividad)

    form = Formulario(
        id_doc=1,
        id_pr=1,
        tipo_formulario=TipoFormulario.FORMULARIO_1,
        estado_de_firma=EstadoFirmaFormulario.PRESENTADO,
        fecha_de_entrega_registro="2026-05-20",
        numero_formulario="FORM-001",
    )
    assert form.tipo_formulario == TipoFormulario.FORMULARIO_1
    assert form.estado_de_firma == EstadoFirmaFormulario.PRESENTADO
    assert isinstance(form.tipo_formulario, TipoFormulario)
    assert isinstance(form.estado_de_firma, EstadoFirmaFormulario)


def test_solicitudes_and_carta_typing():
    """Valida los enums en trámites de empresa propia, oficios y cartas de compromiso."""
    sol_aut = SolicitudAutorizacion(
        id_sol_aut=1,
        id_p_estudiante=2,
        nombre_empresa="Own Corp",
        detalles_empresa="Startup",
        fecha_solicitud="2026-05-10",
        estado_solicitud=EstadoSolicitudAutorizacion.PENDIENTE,
    )
    assert sol_aut.estado_solicitud == EstadoSolicitudAutorizacion.PENDIENTE
    assert isinstance(sol_aut.estado_solicitud, EstadoSolicitudAutorizacion)

    sol_of = SolicitudOficio(
        id_sol_of=1,
        id_p_estudiante=2,
        nombre_destinatario="Gerente",
        cargo_destinatario="CEO",
        nombre_empresa="Own Corp",
        fecha_solicitud="2026-05-10",
        estado_solicitud=EstadoSolicitudOficio.PENDIENTE,
    )
    assert sol_of.estado_solicitud == EstadoSolicitudOficio.PENDIENTE
    assert isinstance(sol_of.estado_solicitud, EstadoSolicitudOficio)

    carta = CartaCompromiso(
        id_carta=1,
        id_pr=1,
        ruta_pdf="storage/documents/carta.pdf",
        estado=EstadoCartaCompromiso.PENDIENTE,
    )
    assert carta.estado == EstadoCartaCompromiso.PENDIENTE
    assert isinstance(carta.estado, EstadoCartaCompromiso)
