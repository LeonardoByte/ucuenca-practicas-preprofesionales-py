"""Módulo 5: Tests unitarios de lógica de negocio (Servicios).

Valida de manera granular todas las reglas de negocio, transiciones de estado, excepciones
personalizadas y flujos de datos para los 11 servicios del sistema.
"""

import pathlib
import shutil

import pytest

# Store original PurePath.__init__ reference
orig_purepath_init = pathlib.PurePath.__init__

def patched_purepath_init(self, *args):
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            new_args.append(arg.replace("storage/db", "storage/test_db").replace("storage\\db", "storage\\test_db"))
        else:
            new_args.append(arg)
    orig_purepath_init(self, *new_args)


# Import models
from src.models import (
    Administrador,
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
    Postulacion,
    Practica,
    RolUsuario,
    TipoFormulario,
    TutorAcademico,
    TutorEmpresarial,
)
from src.services.administrador_main_service import AdministradorMainService

# Import services
from src.services.autenticacion_service import AutenticacionService
from src.services.coordinador_main_service import CoordinadorMainService
from src.services.empresa_main_service import EmpresaMainService
from src.services.estudiante_main_service import EstudianteMainService

# Import exceptions
from src.services.exceptions import (
    CicloNoPermitidoError,
    CorreoDuplicadoError,
    CredencialesInvalidasError,
    DocumentacionIncompletaError,
    EstudianteConPracticaActivaError,
    RequisitosNoCumplidosError,
    TernaInvalidaError,
)
from src.services.login_main_service import LoginMainService
from src.services.oferta_service import OfertaService
from src.services.postulacion_service import PostulacionService
from src.services.practica_service import PracticaService
from src.services.tutor_academico_main_service import TutorAcademicoMainService
from src.services.tutor_empresarial_main_service import TutorEmpresarialMainService

# Import database initializer
from src.utils.inicializador_db import inicializar_todos_los_dat_semilla


@pytest.fixture(autouse=True, scope="module")
def module_redirect_paths():
    """Redirige las rutas de base de datos a storage/test_db únicamente durante la ejecución de este módulo."""
    pathlib.PurePath.__init__ = patched_purepath_init
    yield
    pathlib.PurePath.__init__ = orig_purepath_init


@pytest.fixture(autouse=True)
def clean_test_db():
    import gc
    import time
    gc.collect()
    test_db_dir = pathlib.Path("storage/test_db")
    if test_db_dir.exists():
        for _ in range(5):
            try:
                shutil.rmtree(test_db_dir)
                break
            except Exception:
                time.sleep(0.1)
    yield
    gc.collect()
    if test_db_dir.exists():
        for _ in range(5):
            try:
                shutil.rmtree(test_db_dir)
                break
            except Exception:
                time.sleep(0.1)


# ==========================================
# 1. PRUEBAS DE AUTENTICACION_SERVICE
# ==========================================

def test_autenticacion_verificar_credenciales_usuario_inexistente():
    auth_service = AutenticacionService()
    with pytest.raises(CredencialesInvalidasError):
        auth_service.verificar_credenciales("noexist@unl.edu.ec", "pass123")


def test_autenticacion_verificar_credenciales_contrasena_incorrecta():
    auth_service = AutenticacionService()
    # Crear usuario de prueba
    auth_service.registrar_nuevo_perfil_sistema(
        username_correo="test.user@unl.edu.ec",
        contrasena="correcto",
        rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Test", "ciclo_actual": 6}
    )
    with pytest.raises(CredencialesInvalidasError):
        auth_service.verificar_credenciales("test.user@unl.edu.ec", "incorrecto")


def test_autenticacion_verificar_credenciales_exitoso_roles():
    auth_service = AutenticacionService()
    roles_data = [
        (RolUsuario.ESTUDIANTE, {"nombre_y_apellido": "Estudiante Test", "ciclo_actual": 7}, Estudiante),
        (RolUsuario.COORDINADOR, {"nombre_y_apellido": "Coord Test"}, CoordinadorDePracticas),
        (RolUsuario.TUTOR_ACADEMICO, {"nombre_y_apellido": "Tutor Acad Test"}, TutorAcademico),
        (RolUsuario.TUTOR_EMPRESARIAL, {"nombre_y_apellido": "Tutor Emp Test", "id_e": 1}, TutorEmpresarial),
        (RolUsuario.ADMINISTRADOR, {"nombre_y_apellido": "Admin Test"}, Administrador),
        (RolUsuario.EMPRESARIO, {"nombre_empresa": "Empresa Test", "estado_de_convenio_emp": EstadoConvenio.VIGENTE}, Empresa),
    ]

    for index, (rol, datos, cls) in enumerate(roles_data):
        email = f"user{index}@unl.edu.ec"
        # Registrar
        perfil = auth_service.registrar_nuevo_perfil_sistema(
            username_correo=email,
            contrasena="pass123",
            rol=rol,
            datos_perfil=datos
        )
        assert perfil is not None
        assert isinstance(perfil, cls)

        # Verificar
        logged_in = auth_service.verificar_credenciales(email, "pass123")
        assert logged_in is not None
        assert isinstance(logged_in, cls)


def test_autenticacion_registrar_perfil_correo_duplicado():
    auth_service = AutenticacionService()
    auth_service.registrar_nuevo_perfil_sistema(
        username_correo="dup@unl.edu.ec",
        contrasena="pass123",
        rol=RolUsuario.COORDINADOR,
        datos_perfil={"nombre_y_apellido": "Coord A"}
    )
    with pytest.raises(CorreoDuplicadoError):
        auth_service.registrar_nuevo_perfil_sistema(
            username_correo="dup@unl.edu.ec",
            contrasena="pass456",
            rol=RolUsuario.ESTUDIANTE,
            datos_perfil={"nombre_y_apellido": "Est A"}
        )


def test_autenticacion_eliminar_cuenta_usuario_inexistente():
    auth_service = AutenticacionService()
    assert auth_service.eliminar_cuenta_usuario_sistema("noexist@unl.edu.ec") is False


def test_autenticacion_eliminar_cuenta_usuario_cascada():
    auth_service = AutenticacionService()
    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="del@unl.edu.ec",
        contrasena="pass123",
        rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est Del"}
    )
    assert est is not None
    # Eliminar
    assert auth_service.eliminar_cuenta_usuario_sistema("del@unl.edu.ec") is True
    # Confirmar purgado
    with pytest.raises(CredencialesInvalidasError):
        auth_service.verificar_credenciales("del@unl.edu.ec", "pass123")
    assert auth_service.estudiante_repo.buscar_por_id(est.id_p) is None
    assert auth_service.usuario_repo.buscar_por_username("del@unl.edu.ec") is None


# ==========================================
# 2. PRUEBAS DE ESTUDIANTE_MAIN_SERVICE
# ==========================================

def test_estudiante_catalogo_ofertas_ciclo_bajo():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()

    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="bajo@unl.edu.ec",
        contrasena="pass",
        rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est Bajo", "ciclo_actual": 5}
    )
    with pytest.raises(CicloNoPermitidoError):
        est_service.obtener_catalogo_ofertas(est.id_p)


def test_estudiante_catalogo_prioridad_sin_experiencia():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    emp_service = EmpresaMainService()

    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="noexp@unl.edu.ec",
        contrasena="pass",
        rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est NoExp", "ciclo_actual": 6, "historial_practicas": "Ninguno"}
    )
    # Registrar ofertas y validarlas por coordinador
    o1 = emp_service.registrar_oferta(1, "Oferta 1", "Req", "2026-05-01", "3 meses", 200.0)
    o2 = emp_service.registrar_oferta(1, "Oferta 2", "Req", "2026-05-01", "3 meses", 500.0)
    o3 = emp_service.registrar_oferta(1, "Oferta 3", "Req", "2026-05-01", "3 meses", 350.0)
    o1.validada_por_coordinador = True
    o2.validada_por_coordinador = True
    o3.validada_por_coordinador = True
    emp_service.oferta_service.repo.guardar(o1)
    emp_service.oferta_service.repo.guardar(o2)
    emp_service.oferta_service.repo.guardar(o3)

    catalogo = est_service.obtener_catalogo_ofertas(est.id_p)
    # Sin experiencia ordena por remuneración DESC: 500 -> 350 -> 200
    assert [o.remuneracion for o in catalogo] == [500.0, 350.0, 200.0]


def test_estudiante_catalogo_prioridad_con_experiencia():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    emp_service = EmpresaMainService()

    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="conexp@unl.edu.ec",
        contrasena="pass",
        rol=RolUsuario.ESTUDIANTE,
        datos_perfil={
            "nombre_y_apellido": "Est ConExp",
            "ciclo_actual": 7,
            "historial_practicas": "Práctica en TechCorp",
            "estado_practica": EstadoPracticaEstudiante.FINALIZADA
        }
    )
    # Registrar ofertas y validarlas por coordinador
    o1 = emp_service.registrar_oferta(1, "Oferta 1", "Req", "2026-05-01", "3 meses", 200.0)
    o2 = emp_service.registrar_oferta(1, "Oferta 2", "Req", "2026-05-01", "3 meses", 500.0)
    o3 = emp_service.registrar_oferta(1, "Oferta 3", "Req", "2026-05-01", "3 meses", 350.0)
    o1.validada_por_coordinador = True
    o2.validada_por_coordinador = True
    o3.validada_por_coordinador = True
    emp_service.oferta_service.repo.guardar(o1)
    emp_service.oferta_service.repo.guardar(o2)
    emp_service.oferta_service.repo.guardar(o3)

    catalogo = est_service.obtener_catalogo_ofertas(est.id_p)
    # Con experiencia ordena por remuneración ASC: 200 -> 350 -> 500
    assert [o.remuneracion for o in catalogo] == [200.0, 350.0, 500.0]


def test_estudiante_solicitar_postulacion_ciclo_bajo():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="bajo2@unl.edu.ec",
        contrasena="pass",
        rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est Bajo", "ciclo_actual": 4, "estado_de_matricula": EstadoMatricula.MATRICULADO}
    )
    with pytest.raises(RequisitosNoCumplidosError):
        est_service.solicitar_postulacion(est.id_p, 1, 1, "2026-05-29")


def test_estudiante_solicitar_postulacion_no_matriculado():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="nomat@unl.edu.ec",
        contrasena="pass",
        rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est NoMat", "ciclo_actual": 7, "estado_de_matricula": EstadoMatricula.NO_MATRICULADO}
    )
    with pytest.raises(RequisitosNoCumplidosError):
        est_service.solicitar_postulacion(est.id_p, 1, 1, "2026-05-29")


def test_estudiante_solicitar_postulacion_practica_activa():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="activa@unl.edu.ec",
        contrasena="pass",
        rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est Activa", "ciclo_actual": 7, "estado_de_matricula": EstadoMatricula.MATRICULADO, "estado_practica": EstadoPracticaEstudiante.ACTIVA}
    )
    with pytest.raises(EstudianteConPracticaActivaError):
        est_service.solicitar_postulacion(est.id_p, 1, 1, "2026-05-29")


def test_estudiante_solicitar_postulacion_exitosa():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="ok@unl.edu.ec",
        contrasena="pass",
        rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est Ok", "ciclo_actual": 7, "estado_de_matricula": EstadoMatricula.MATRICULADO, "estado_practica": EstadoPracticaEstudiante.SIN_PRACTICAS}
    )
    post = est_service.solicitar_postulacion(est.id_p, 10, 5, "2026-05-29")
    assert post is not None
    assert post.id_p_estudiante == est.id_p
    assert post.id_o == 10
    assert post.estado_de_postulacion == EstadoPostulacion.PENDIENTE


def test_estudiante_registrar_solicitud_autorizacion():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="aut@unl.edu.ec", contrasena="pass", rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est Aut"}
    )
    sol = est_service.registrar_solicitud_autorizacion(est.id_p, "Empresa A", "Desarrollo Python", "2026-05-20")
    assert sol is not None
    assert sol.id_p_estudiante == est.id_p
    assert sol.nombre_empresa == "Empresa A"
    assert sol.estado_solicitud == "Pendiente"


def test_estudiante_registrar_solicitud_oficio():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="of@unl.edu.ec", contrasena="pass", rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est Of"}
    )
    sol = est_service.registrar_solicitud_oficio(est.id_p, "Dr. Gomez", "Director de Carrera", "Empresa B", "2026-05-20")
    assert sol is not None
    assert sol.id_p_estudiante == est.id_p
    assert sol.nombre_destinatario == "Dr. Gomez"
    assert sol.estado_solicitud == "Pendiente"


def test_estudiante_registrar_actividad_bitacora():
    est_service = EstudianteMainService()
    act = est_service.registrar_actividad_bitacora(5, "Redacción de documentación técnica")
    assert act is not None
    assert act.id_pr == 5
    assert act.descripcion_de_la_tarea == "Redacción de documentación técnica"
    assert act.estado_de_validacion == EstadoValidacionActividad.PROPUESTA


# ==========================================
# 3. PRUEBAS DE COORDINADOR_MAIN_SERVICE
# ==========================================

def test_coordinador_revisar_postulaciones_pendientes():
    inicializar_todos_los_dat_semilla()
    coord_service = CoordinadorMainService()
    est_service = EstudianteMainService()

    # Añadir postulaciones
    est_service.solicitar_postulacion(1, 10, 5, "2026-05-29")
    est_service.solicitar_postulacion(1, 11, 5, "2026-05-29")

    pendientes = coord_service.revisar_postulaciones_pendientes()
    assert len(pendientes) == 2
    assert all(p.estado_de_postulacion == EstadoPostulacion.PENDIENTE for p in pendientes)


def test_coordinador_validar_requisitos_alumno():
    coord_service = CoordinadorMainService()
    est_service = EstudianteMainService()
    inicializar_todos_los_dat_semilla()

    post = est_service.solicitar_postulacion(1, 10, 5, "2026-05-29")

    # Validar Aprobado -> cambia a VALIDADA
    res1 = coord_service.validar_requisitos_alumno(post.id_pos, aprobado=True)
    assert res1 is True
    post_up = coord_service.postulacion_repo.buscar_por_id(post.id_pos)
    assert post_up.estado_de_postulacion == EstadoPostulacion.VALIDADA

    # Validar Rechazado -> cambia a RECHAZADA
    res2 = coord_service.validar_requisitos_alumno(post.id_pos, aprobado=False)
    assert res2 is True
    post_up = coord_service.postulacion_repo.buscar_por_id(post.id_pos)
    assert post_up.estado_de_postulacion == EstadoPostulacion.RECHAZADA


def test_coordinador_enviar_terna_conteo_invalido():
    coord_service = CoordinadorMainService()
    with pytest.raises(TernaInvalidaError):
        coord_service.enviar_terna_a_empresa([1, 2])


def test_coordinador_enviar_terna_ofertas_distintas():
    coord_service = CoordinadorMainService()
    est_service = EstudianteMainService()
    inicializar_todos_los_dat_semilla()

    p1 = est_service.solicitar_postulacion(1, 10, 5, "2026-05-29")
    p2 = est_service.solicitar_postulacion(1, 10, 5, "2026-05-29")
    p3 = est_service.solicitar_postulacion(1, 11, 5, "2026-05-29")  # Otra oferta

    with pytest.raises(TernaInvalidaError):
        coord_service.enviar_terna_a_empresa([p1.id_pos, p2.id_pos, p3.id_pos])


def test_coordinador_enviar_terna_exitosa_e_id_autoincremental():
    coord_service = CoordinadorMainService()
    est_service = EstudianteMainService()
    inicializar_todos_los_dat_semilla()

    p1 = est_service.solicitar_postulacion(1, 10, 5, "2026-05-29")
    p2 = est_service.solicitar_postulacion(1, 10, 5, "2026-05-29")
    p3 = est_service.solicitar_postulacion(1, 10, 5, "2026-05-29")

    # Primera terna
    assert coord_service.enviar_terna_a_empresa([p1.id_pos, p2.id_pos, p3.id_pos]) is True
    p1_up = coord_service.postulacion_repo.buscar_por_id(p1.id_pos)
    assert p1_up.id_terna == 1

    # Segunda terna
    p4 = est_service.solicitar_postulacion(1, 20, 6, "2026-05-29")
    p5 = est_service.solicitar_postulacion(1, 20, 6, "2026-05-29")
    p6 = est_service.solicitar_postulacion(1, 20, 6, "2026-05-29")
    assert coord_service.enviar_terna_a_empresa([p4.id_pos, p5.id_pos, p6.id_pos]) is True
    p4_up = coord_service.postulacion_repo.buscar_por_id(p4.id_pos)
    assert p4_up.id_terna == 2


def test_coordinador_asignar_tutor_a_practica():
    coord_service = CoordinadorMainService()
    practica_service = PracticaService()

    # Crear una práctica ficticia
    practica = practica_service.practica_repo.guardar(
        Practica(id_pr=1, id_pos=1, id_p_tutor_acad=0, id_p_tutor_emp=1, fecha_inicio="2026-06-01", fecha_fin="2026-12-01", estado_de_practica=EstadoPractica.INICIADA)
    )
    assert coord_service.asignar_tutor_a_practica(1, 10) is True
    pr_up = coord_service.practica_repo.buscar_por_id(1)
    assert pr_up.id_p_tutor_acad == 10


def test_coordinador_cierre_oficial_practica_inexistente():
    coord_service = CoordinadorMainService()
    assert coord_service.ejecutar_cierre_oficial_practica(999) is False


def test_coordinador_cierre_oficial_documentacion_incompleta_formularios():
    coord_service = CoordinadorMainService()
    practica_service = PracticaService()
    inicializar_todos_los_dat_semilla()

    # Guardar práctica
    practica_service.practica_repo.guardar(
        Practica(id_pr=1, id_pos=1, id_p_tutor_acad=10, id_p_tutor_emp=1, fecha_inicio="2026-06-01", fecha_fin="2026-12-01", estado_de_practica=EstadoPractica.INICIADA)
    )
    # Rellenar solo Formulario 1 y 2
    practica_service.actualizar_formulario(1, TipoFormulario.FORMULARIO_1, EstadoFirmaFormulario.COMPLETADO, "2026-06-15", "F1")
    practica_service.actualizar_formulario(1, TipoFormulario.FORMULARIO_2, EstadoFirmaFormulario.COMPLETADO, "2026-06-25", "F2")
    # Carta firmada
    practica_service.registrar_entrega_carta_compromiso(1, "carta.pdf", EstadoCartaCompromiso.FIRMADA)

    with pytest.raises(DocumentacionIncompletaError):
        coord_service.ejecutar_cierre_oficial_practica(1)


def test_coordinador_cierre_oficial_documentacion_incompleta_carta():
    coord_service = CoordinadorMainService()
    practica_service = PracticaService()
    inicializar_todos_los_dat_semilla()

    # Guardar práctica
    practica_service.practica_repo.guardar(
        Practica(id_pr=1, id_pos=1, id_p_tutor_acad=10, id_p_tutor_emp=1, fecha_inicio="2026-06-01", fecha_fin="2026-12-01", estado_de_practica=EstadoPractica.INICIADA)
    )
    # Todos los formularios completados
    practica_service.actualizar_formulario(1, TipoFormulario.FORMULARIO_1, EstadoFirmaFormulario.COMPLETADO, "2026-06-15", "F1")
    practica_service.actualizar_formulario(1, TipoFormulario.FORMULARIO_2, EstadoFirmaFormulario.COMPLETADO, "2026-06-25", "F2")
    practica_service.actualizar_formulario(1, TipoFormulario.FORMULARIO_3, EstadoFirmaFormulario.COMPLETADO, "2026-06-30", "F3")
    # Carta solo ENTEGRADA (no firmada)
    practica_service.registrar_entrega_carta_compromiso(1, "carta.pdf", EstadoCartaCompromiso.ENTREGADA)

    with pytest.raises(DocumentacionIncompletaError):
        coord_service.ejecutar_cierre_oficial_practica(1)


def test_coordinador_cierre_oficial_exitoso():
    coord_service = CoordinadorMainService()
    practica_service = PracticaService()
    inicializar_todos_los_dat_semilla()

    # Postulación y práctica
    post = Postulacion(id_pos=1, id_p_estudiante=1, id_o=1, id_e=1, id_p_coordinador=1, fecha_postulacion="2026-05-29", estado_de_postulacion=EstadoPostulacion.ACEPTADA)
    coord_service.postulacion_repo.guardar(post)

    practica_service.practica_repo.guardar(
        Practica(id_pr=1, id_pos=1, id_p_tutor_acad=10, id_p_tutor_emp=1, fecha_inicio="2026-06-01", fecha_fin="2026-12-01", estado_de_practica=EstadoPractica.INICIADA)
    )

    # Documentación completada
    practica_service.actualizar_formulario(1, TipoFormulario.FORMULARIO_1, EstadoFirmaFormulario.COMPLETADO, "2026-06-15", "F1")
    practica_service.actualizar_formulario(1, TipoFormulario.FORMULARIO_2, EstadoFirmaFormulario.COMPLETADO, "2026-06-25", "F2")
    practica_service.actualizar_formulario(1, TipoFormulario.FORMULARIO_3, EstadoFirmaFormulario.COMPLETADO, "2026-06-30", "F3")
    practica_service.registrar_entrega_carta_compromiso(1, "carta.pdf", EstadoCartaCompromiso.FIRMADA)

    assert coord_service.ejecutar_cierre_oficial_practica(1) is True

    # Verificar estado de práctica -> APROBADA
    pr = coord_service.practica_repo.buscar_por_id(1)
    assert pr.estado_de_practica == EstadoPractica.APROBADA

    # Verificar estado del estudiante -> FINALIZADA
    est = coord_service.estudiante_repo.buscar_por_id(1)
    assert est.estado_practica == EstadoPracticaEstudiante.FINALIZADA


# ==========================================
# 4. PRUEBAS DE EMPRESA_MAIN_SERVICE
# ==========================================

def test_empresa_registrar_oferta():
    emp_service = EmpresaMainService()
    oferta = emp_service.registrar_oferta(1, "Desarrollo", "Reqs", "2026-05-01", "6 meses", 400.0)
    assert oferta is not None
    assert oferta.id_e == 1
    assert oferta.descripcion_oferta == "Desarrollo"


def test_empresa_visualizar_terna_recibida():
    emp_service = EmpresaMainService()
    post_service = PostulacionService()
    inicializar_todos_los_dat_semilla()

    # Registrar postulaciones y agrupar en terna 1
    p1 = post_service.registrar_postulacion(1, 10, 5, 1, "2026-05-29")
    p2 = post_service.registrar_postulacion(2, 10, 5, 1, "2026-05-29")
    p3 = post_service.registrar_postulacion(3, 10, 5, 1, "2026-05-29")
    post_service.cambiar_estado(p1.id_pos, EstadoPostulacion.VALIDADA)
    post_service.cambiar_estado(p2.id_pos, EstadoPostulacion.VALIDADA)
    post_service.cambiar_estado(p3.id_pos, EstadoPostulacion.VALIDADA)
    post_service.agrupar_y_despachar_terna([p1.id_pos, p2.id_pos, p3.id_pos])

    terna = emp_service.visualizar_terna_recibida(1)
    assert len(terna) == 3
    assert all(p.id_terna == 1 for p in terna)


def test_empresa_seleccionar_candidato_ganador_exitoso():
    emp_service = EmpresaMainService()
    post_service = PostulacionService()
    inicializar_todos_los_dat_semilla()

    # Terna
    p1 = post_service.registrar_postulacion(1, 10, 5, 1, "2026-05-29")
    p2 = post_service.registrar_postulacion(2, 10, 5, 1, "2026-05-29")
    p3 = post_service.registrar_postulacion(3, 10, 5, 1, "2026-05-29")
    post_service.agrupar_y_despachar_terna([p1.id_pos, p2.id_pos, p3.id_pos])

    # Seleccionar p1
    assert emp_service.seleccionar_candidato_ganador(p1.id_pos, 10, "2026-06-01", "2026-12-01") is True

    # Verificar que p1 es Aceptada, y p2 y p3 son Rechazadas
    p1_up = post_service.buscar_postulacion_por_id(p1.id_pos)
    p2_up = post_service.buscar_postulacion_por_id(p2.id_pos)
    p3_up = post_service.buscar_postulacion_por_id(p3.id_pos)

    assert p1_up.estado_de_postulacion == EstadoPostulacion.ACEPTADA
    assert p2_up.estado_de_postulacion == EstadoPostulacion.RECHAZADA
    assert p3_up.estado_de_postulacion == EstadoPostulacion.RECHAZADA


# ==========================================
# 5. PRUEBAS DE TUTORES (ACADEMICO / EMPRESARIAL)
# ==========================================

def test_tutor_academico_evaluar_actividad_alumno():
    tutor_service = TutorAcademicoMainService()
    practica_service = PracticaService()

    act = practica_service.registrar_actividad(1, "Actividad 1")
    assert act.estado_de_validacion == EstadoValidacionActividad.PROPUESTA

    assert tutor_service.evaluar_actividad_alumno(act.id_act, 1, EstadoValidacionActividad.VALIDADA) is True
    act_up = practica_service.actividad_repo.buscar_por_id(act.id_act)
    assert act_up.estado_de_validacion == EstadoValidacionActividad.VALIDADA


def test_tutor_academico_registrar_evaluacion_formulario2():
    tutor_service = TutorAcademicoMainService()
    practica_service = PracticaService()
    inicializar_todos_los_dat_semilla()

    # Guardar práctica que vence el 2026-06-30
    practica_service.practica_repo.guardar(
        Practica(id_pr=1, id_pos=1, id_p_tutor_acad=10, id_p_tutor_emp=1, fecha_inicio="2026-06-01", fecha_fin="2026-06-30", estado_de_practica=EstadoPractica.INICIADA)
    )

    # Registro exitoso (dentro de los 7 días)
    assert tutor_service.registrar_evaluacion_formulario2(1, EstadoFirmaFormulario.COMPLETADO, "2026-06-25") is True
    forms = practica_service.formulario_repo.listar_formularios_por_practica(1)
    f2 = [f for f in forms if f.tipo_formulario == TipoFormulario.FORMULARIO_2][0]
    assert f2.estado_de_firma == EstadoFirmaFormulario.COMPLETADO
    assert f2.fecha_de_entrega_registro == "2026-06-25"

    # Registro fallido por evaluación temprana
    from src.services.exceptions import EvaluacionTempranaError
    with pytest.raises(EvaluacionTempranaError):
        tutor_service.registrar_evaluacion_formulario2(1, EstadoFirmaFormulario.COMPLETADO, "2026-06-20")


def test_tutor_empresarial_registrar_evaluacion_formulario3():
    tutor_emp_service = TutorEmpresarialMainService()
    practica_service = PracticaService()
    inicializar_todos_los_dat_semilla()

    # Guardar práctica que vence el 2026-06-30
    practica_service.practica_repo.guardar(
        Practica(id_pr=1, id_pos=1, id_p_tutor_acad=10, id_p_tutor_emp=1, fecha_inicio="2026-06-01", fecha_fin="2026-06-30", estado_de_practica=EstadoPractica.INICIADA)
    )

    # Registro exitoso (dentro de los 7 días)
    assert tutor_emp_service.registrar_evaluacion_formulario3(1, EstadoFirmaFormulario.COMPLETADO, "2026-06-26") is True
    forms = practica_service.formulario_repo.listar_formularios_por_practica(1)
    f3 = [f for f in forms if f.tipo_formulario == TipoFormulario.FORMULARIO_3][0]
    assert f3.estado_de_firma == EstadoFirmaFormulario.COMPLETADO
    assert f3.fecha_de_entrega_registro == "2026-06-26"

    # Registro fallido por evaluación temprana
    from src.services.exceptions import EvaluacionTempranaError
    with pytest.raises(EvaluacionTempranaError):
        tutor_emp_service.registrar_evaluacion_formulario3(1, EstadoFirmaFormulario.COMPLETADO, "2026-06-20")


# ==========================================
# 6. PRUEBAS DE SERVICIOS DE APOYO
# ==========================================

def test_login_main_service_ejecutar_ingreso_exitoso():
    inicializar_todos_los_dat_semilla()
    login_service = LoginMainService()

    # login exitoso del administrador
    profile, rol = login_service.ejecutar_ingreso("sofia.ramirez@unl.edu.ec", "pass123")
    assert profile is not None
    assert isinstance(profile, Administrador)
    assert rol == "Administrador"


def test_login_main_service_ejecutar_ingreso_fallido():
    inicializar_todos_los_dat_semilla()
    login_service = LoginMainService()

    profile, rol = login_service.ejecutar_ingreso("sofia.ramirez@unl.edu.ec", "wrong")
    assert profile is None
    assert rol == ""


def test_oferta_service_crear_y_buscar():
    oferta_service = OfertaService()
    o = oferta_service.crear_oferta(5, "Pasantía IA", "Maths", "2026-05-29", "4 meses", 550.0)
    assert o is not None

    fetched = oferta_service.buscar_oferta_por_id(o.id_o)
    assert fetched is not None
    assert fetched.descripcion_oferta == "Pasantía IA"
    assert fetched.remuneracion == 550.0


def test_postulacion_service_cambiar_estado():
    post_service = PostulacionService()
    inicializar_todos_los_dat_semilla()

    post = post_service.registrar_postulacion(1, 10, 5, None, "2026-05-29")
    assert post.estado_de_postulacion == EstadoPostulacion.PENDIENTE

    assert post_service.cambiar_estado(post.id_pos, EstadoPostulacion.VALIDADA) is True
    post_up = post_service.buscar_postulacion_por_id(post.id_pos)
    assert post_up.estado_de_postulacion == EstadoPostulacion.VALIDADA


def test_practica_service_formalizar_error_estudiante_con_practica_activa():
    auth_service = AutenticacionService()
    practica_service = PracticaService()
    inicializar_todos_los_dat_semilla()

    # Registrar estudiante con práctica activa
    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="hasactive@unl.edu.ec", contrasena="pass", rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est Active", "ciclo_actual": 7, "estado_de_matricula": EstadoMatricula.MATRICULADO, "estado_practica": EstadoPracticaEstudiante.ACTIVA}
    )

    # Crear una postulación
    post = Postulacion(id_pos=10, id_p_estudiante=est.id_p, id_o=1, id_e=1, id_p_coordinador=1, fecha_postulacion="2026-05-29", estado_de_postulacion=EstadoPostulacion.VALIDADA)
    practica_service.postulacion_repo.guardar(post)

    with pytest.raises(EstudianteConPracticaActivaError):
        practica_service.formalizar_practica(post.id_pos, 2, "2026-06-01", "2026-12-01")


def test_administrador_crear_y_eliminar_perfil():
    admin_service = AdministradorMainService()
    inicializar_todos_los_dat_semilla()

    profile = admin_service.crear_cuenta_usuario_sistema(
        username_correo="newadmin@unl.edu.ec", contrasena="pass", rol=RolUsuario.ADMINISTRADOR, datos_perfil={"nombre_y_apellido": "New Admin"}
    )
    assert profile is not None
    assert isinstance(profile, Administrador)

    assert admin_service.eliminar_usuario_sistema("newadmin@unl.edu.ec") is True


def test_empresa_listar_mis_ofertas_publicadas():
    emp_service = EmpresaMainService()
    inicializar_todos_los_dat_semilla()

    emp_service.registrar_oferta(10, "Python Developer", "Requirements", "2026-05-30", "3 meses", 500.0)
    emp_service.registrar_oferta(10, "FastAPI Developer", "Requirements", "2026-05-30", "6 meses", 600.0)
    emp_service.registrar_oferta(20, "Other Company Job", "Requirements", "2026-05-30", "3 meses", 400.0)

    ofertas = emp_service.listar_mis_ofertas_publicadas(10)
    assert len(ofertas) == 2
    assert all(o.id_e == 10 for o in ofertas)


def test_estudiante_listar_mis_solicitudes_historial():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    inicializar_todos_los_dat_semilla()

    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="solhist@unl.edu.ec", contrasena="pass", rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est Hist"}
    )

    est_service.registrar_solicitud_autorizacion(est.id_p, "Company A", "Details A", "2026-05-30")
    est_service.registrar_solicitud_oficio(est.id_p, "Dr. Smith", "Director", "Company B", "2026-05-30")

    sol_aut = est_service.obtener_mis_solicitudes_autorizacion(est.id_p)
    sol_of = est_service.obtener_mis_solicitudes_oficio(est.id_p)

    assert len(sol_aut) == 1
    assert sol_aut[0].nombre_empresa == "Company A"
    assert len(sol_of) == 1
    assert sol_of[0].nombre_destinatario == "Dr. Smith"


def test_coordinador_listar_solicitudes_pendientes():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    coord_service = CoordinadorMainService()
    inicializar_todos_los_dat_semilla()

    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="coordhist@unl.edu.ec", contrasena="pass", rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Est CoordHist"}
    )

    est_service.registrar_solicitud_autorizacion(est.id_p, "Company A", "Details A", "2026-05-30")
    est_service.registrar_solicitud_oficio(est.id_p, "Dr. Smith", "Director", "Company B", "2026-05-30")

    sol_aut_pend = coord_service.listar_solicitudes_autorizacion_pendientes()
    sol_of_pend = coord_service.listar_solicitudes_oficio_pendientes()

    assert len(sol_aut_pend) == 1
    assert sol_aut_pend[0].estado_solicitud == EstadoSolicitudAutorizacion.PENDIENTE
    assert len(sol_of_pend) == 1
    assert sol_of_pend[0].estado_solicitud == EstadoSolicitudOficio.PENDIENTE


def test_practica_service_formalizar_rechazo_masivo_y_formulario1():
    auth_service = AutenticacionService()
    est_service = EstudianteMainService()
    practica_service = PracticaService()
    inicializar_todos_los_dat_semilla()

    # Registrar el estudiante
    est = auth_service.registrar_nuevo_perfil_sistema(
        username_correo="studwinner@unl.edu.ec", contrasena="pass", rol=RolUsuario.ESTUDIANTE,
        datos_perfil={"nombre_y_apellido": "Winner Stud", "ciclo_actual": 7, "estado_de_matricula": EstadoMatricula.MATRICULADO}
    )

    # Crear 3 postulaciones para este estudiante (ofertas diferentes)
    p1 = est_service.solicitar_postulacion(est.id_p, 100, 10, "2026-05-30")
    p2 = est_service.solicitar_postulacion(est.id_p, 200, 10, "2026-05-30")
    p3 = est_service.solicitar_postulacion(est.id_p, 300, 10, "2026-05-30")

    # Validar todas las postulaciones
    post_service = PostulacionService()
    post_service.cambiar_estado(p1.id_pos, EstadoPostulacion.VALIDADA)
    post_service.cambiar_estado(p2.id_pos, EstadoPostulacion.VALIDADA)
    post_service.cambiar_estado(p3.id_pos, EstadoPostulacion.VALIDADA)

    # Formalizar la práctica aceptando p1
    practica = practica_service.formalizar_practica(p1.id_pos, 50, "2026-06-01", "2026-12-01")
    assert practica is not None

    # Verificar que p1 es ACEPTADA y p2, p3 son RECHAZADA (rechazo masivo de postulaciones activas)
    p1_up = post_service.buscar_postulacion_por_id(p1.id_pos)
    p2_up = post_service.buscar_postulacion_por_id(p2.id_pos)
    p3_up = post_service.buscar_postulacion_por_id(p3.id_pos)

    assert p1_up.estado_de_postulacion == EstadoPostulacion.ACEPTADA
    assert p2_up.estado_de_postulacion == EstadoPostulacion.RECHAZADA
    assert p3_up.estado_de_postulacion == EstadoPostulacion.RECHAZADA

    # Verificar que el Formulario 1 fue registrado automáticamente en estado PRESENTADO
    forms = practica_service.formulario_repo.listar_formularios_por_practica(practica.id_pr)
    f1 = [f for f in forms if f.tipo_formulario == TipoFormulario.FORMULARIO_1][0]
    assert f1.estado_de_firma == EstadoFirmaFormulario.PRESENTADO
