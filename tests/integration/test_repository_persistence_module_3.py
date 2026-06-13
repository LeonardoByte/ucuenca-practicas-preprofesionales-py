# ruff: noqa: E402, E501
import shutil
from pathlib import Path

import pytest

# 1. Define TEST_DB_DIR
TEST_DB_DIR = Path("storage/test_db")

# 2. Patch serialization BEFORE importing repository classes to bind imports to patched functions
import src.utils.serialization

_original_load = src.utils.serialization.load_db_dat
_original_save = src.utils.serialization.save_db_dat

def patched_load(filepath):
    redirected = TEST_DB_DIR / Path(filepath).name
    return _original_load(redirected)

def patched_save(filepath, datos):
    redirected = TEST_DB_DIR / Path(filepath).name
    return _original_save(redirected, datos)

src.utils.serialization.load_db_dat = patched_load
src.utils.serialization.save_db_dat = patched_save

# 3. Now import repository classes and models
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
    Oferta,
    Postulacion,
    Practica,
    RolUsuario,
    SolicitudAutorizacion,
    SolicitudOficio,
    TipoFormulario,
    TutorAcademico,
    TutorEmpresarial,
    Usuario,
)
from src.repositories.actividad_repository import ActividadRepository
from src.repositories.administrador_repository import AdministradorRepository
from src.repositories.carta_compromiso_repository import CartaCompromisoRepository
from src.repositories.convenio_repository import ConvenioRepository
from src.repositories.coordinador_repository import CoordinadorRepository
from src.repositories.empresa_repository import EmpresaRepository
from src.repositories.estudiante_repository import EstudianteRepository
from src.repositories.formulario_repository import FormularioRepository
from src.repositories.oferta_repository import OfertaRepository
from src.repositories.postulacion_repository import PostulacionRepository
from src.repositories.practica_repository import PracticaRepository
from src.repositories.solicitud_autorizacion_repository import SolicitudAutorizacionRepository
from src.repositories.solicitud_oficio_repository import SolicitudOficioRepository
from src.repositories.tutor_academico_repository import TutorAcademicoRepository
from src.repositories.tutor_empresarial_repository import TutorEmpresarialRepository
from src.repositories.usuario_repository import UsuarioRepository


# 4. Patch __init__ for repositories
def make_custom_init(repo_cls):
    original_init = repo_cls.__init__
    def custom_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        if hasattr(self, 'filepath'):
            self.filepath = TEST_DB_DIR / self.filepath.name
    return custom_init

for repo_cls in [
    ActividadRepository, AdministradorRepository, CartaCompromisoRepository, ConvenioRepository,
    CoordinadorRepository, EmpresaRepository, EstudianteRepository, FormularioRepository,
    OfertaRepository, PostulacionRepository, PracticaRepository, SolicitudAutorizacionRepository,
    SolicitudOficioRepository, TutorAcademicoRepository, TutorEmpresarialRepository, UsuarioRepository
]:
    repo_cls.__init__ = make_custom_init(repo_cls)

@pytest.fixture(scope="module", autouse=True)
def patch_serialization():
    yield
    src.utils.serialization.load_db_dat = _original_load
    src.utils.serialization.save_db_dat = _original_save


@pytest.fixture(autouse=True)
def clean_test_db():
    if TEST_DB_DIR.exists():
        shutil.rmtree(TEST_DB_DIR)
    TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
    yield
    if TEST_DB_DIR.exists():
        shutil.rmtree(TEST_DB_DIR)


def test_actividad_repository():
    repo = ActividadRepository()

    # 1. Nonexistent file resilience
    assert repo.buscar_por_id(999) is None
    assert repo.listar_por_practica(999) == []
    assert repo.obtener_todos() == []

    # 2. Folder and file creation on save (zero-failure)
    act = Actividad(id_act=None, id_pr=10, descripcion_de_la_tarea="Hacer pruebas", estado_de_validacion=EstadoValidacionActividad.PROPUESTA)
    assert repo.guardar(act) is True
    assert (TEST_DB_DIR / "actividades.dat").exists()

    # 3. Auto-increment checks (None, 0, negative)
    assert act.id_act == 1

    act2 = Actividad(id_act=0, id_pr=10, descripcion_de_la_tarea="Documentar", estado_de_validacion=EstadoValidacionActividad.PROPUESTA)
    assert repo.guardar(act2) is True
    assert act2.id_act == 2

    act3 = Actividad(id_act=-9, id_pr=10, descripcion_de_la_tarea="Refactorizar", estado_de_validacion=EstadoValidacionActividad.PROPUESTA)
    assert repo.guardar(act3) is True
    assert act3.id_act == 3

    # 4. Try saving positive ID that does not exist (returns False for ActividadRepository)
    act_non_existent = Actividad(id_act=99, id_pr=10, descripcion_de_la_tarea="Invalida", estado_de_validacion=EstadoValidacionActividad.PROPUESTA)
    assert repo.guardar(act_non_existent) is False

    # 5. Retrieve and update
    repo2 = ActividadRepository()
    loaded = repo2.buscar_por_id(2)
    assert loaded is not None
    assert loaded.descripcion_de_la_tarea == "Documentar"

    loaded.descripcion_de_la_tarea = "Documentar v2"
    assert repo2.guardar(loaded) is True

    # Verify update persisted
    repo3 = ActividadRepository()
    assert repo3.buscar_por_id(2).descripcion_de_la_tarea == "Documentar v2"

    # 6. Specific searches
    acts = repo3.listar_por_practica(10)
    assert len(acts) == 3
    assert {a.id_act for a in acts} == {1, 2, 3}

    # 7. Delete
    assert repo3.eliminar(2) is True
    assert repo3.buscar_por_id(2) is None
    assert len(repo3.listar_por_practica(10)) == 2


def test_administrador_repository():
    repo = AdministradorRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.buscar_persona_por_id(999) is None
    assert repo.obtener_todos() == []

    # Save creates file
    admin = Administrador(id_p=None, nombre_y_apellido="Sofia Ramirez", cedula_dni="1745678901", correo_electronico="sofia@unl.edu.ec", direccion="Loja")
    assert repo.guardar(admin) is True
    assert (TEST_DB_DIR / "administradores.dat").exists()
    assert admin.id_p == 1

    # Auto-increment
    admin2 = Administrador(id_p=0, nombre_y_apellido="Alex Doe", cedula_dni="1234567890", correo_electronico="alex@unl.edu.ec", direccion="Loja")
    assert repo.guardar(admin2) is True
    assert admin2.id_p == 2

    admin3 = Administrador(id_p=-1, nombre_y_apellido="Carlos M.", cedula_dni="1723456789", correo_electronico="carlos@unl.edu.ec", direccion="Loja")
    assert repo.guardar(admin3) is True
    assert admin3.id_p == 3

    # Load and update
    repo2 = AdministradorRepository()
    loaded = repo2.buscar_por_id(2)
    assert loaded is not None
    assert loaded.nombre_y_apellido == "Alex Doe"

    loaded.nombre_y_apellido = "Alex Doe Updated"
    assert repo2.guardar(loaded) is True

    repo3 = AdministradorRepository()
    assert repo3.buscar_por_id(2).nombre_y_apellido == "Alex Doe Updated"

    # Specific searches
    assert repo3.buscar_persona_por_id(2) is not None
    assert repo3.buscar_persona_por_id(2).nombre_y_apellido == "Alex Doe Updated"

    # Delete
    assert repo3.eliminar(2) is True
    assert repo3.buscar_por_id(2) is None


def test_carta_compromiso_repository():
    repo = CartaCompromisoRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.buscar_por_practica(999) is None
    assert repo.obtener_todos() == []

    carta = CartaCompromiso(id_carta=None, id_pr=100, ruta_pdf="carta.pdf", estado=EstadoCartaCompromiso.PENDIENTE)
    assert repo.guardar(carta) is True
    assert (TEST_DB_DIR / "cartas_compromiso.dat").exists()
    assert carta.id_carta == 1

    # Auto-increment
    carta2 = CartaCompromiso(id_carta=0, id_pr=101, ruta_pdf="carta2.pdf", estado=EstadoCartaCompromiso.PENDIENTE)
    assert repo.guardar(carta2) is True
    assert carta2.id_carta == 2

    carta3 = CartaCompromiso(id_carta=-10, id_pr=102, ruta_pdf="carta3.pdf", estado=EstadoCartaCompromiso.PENDIENTE)
    assert repo.guardar(carta3) is True
    assert carta3.id_carta == 3

    # Load and update
    repo2 = CartaCompromisoRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.ruta_pdf == "carta.pdf"

    loaded.ruta_pdf = "carta_updated.pdf"
    assert repo2.guardar(loaded) is True

    repo3 = CartaCompromisoRepository()
    assert repo3.buscar_por_id(1).ruta_pdf == "carta_updated.pdf"

    # Specific searches
    assert repo3.buscar_por_practica(101).id_carta == 2

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_convenio_repository():
    repo = ConvenioRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.buscar_por_empresa(999) is None
    assert repo.obtener_todos() == []

    conv = Convenio(id_con=None, id_e=50, fecha_firma="2026-01-01", fecha_vencimiento="2027-01-01", estado_del_convenio=EstadoConvenio.VIGENTE)
    assert repo.guardar(conv) is True
    assert (TEST_DB_DIR / "convenios.dat").exists()
    assert conv.id_con == 1

    # Auto-increment
    conv2 = Convenio(id_con=0, id_e=51, fecha_firma="2026-01-01", fecha_vencimiento="2027-01-01", estado_del_convenio=EstadoConvenio.VIGENTE)
    assert repo.guardar(conv2) is True
    assert conv2.id_con == 2

    conv3 = Convenio(id_con=-1, id_e=52, fecha_firma="2026-01-01", fecha_vencimiento="2027-01-01", estado_del_convenio=EstadoConvenio.VIGENTE)
    assert repo.guardar(conv3) is True
    assert conv3.id_con == 3

    # Load and update
    repo2 = ConvenioRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.fecha_firma == "2026-01-01"

    loaded.fecha_firma = "2026-02-02"
    assert repo2.guardar(loaded) is True

    repo3 = ConvenioRepository()
    assert repo3.buscar_por_id(1).fecha_firma == "2026-02-02"

    # Specific searches
    assert repo3.buscar_por_empresa(51).id_con == 2

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_coordinador_repository():
    repo = CoordinadorRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.obtener_todos() == []

    coord = CoordinadorDePracticas(id_p=None, nombre_y_apellido="Ana Nuñez", cedula_dni="1798765431", correo_electronico="ana@unl.edu.ec", direccion="Loja")
    assert repo.guardar(coord) is True
    assert (TEST_DB_DIR / "coordinadores.dat").exists()
    assert coord.id_p == 1

    # Auto-increment
    coord2 = CoordinadorDePracticas(id_p=0, nombre_y_apellido="Ana Nuñez 2", cedula_dni="1798765432", correo_electronico="ana2@unl.edu.ec", direccion="Loja")
    assert repo.guardar(coord2) is True
    assert coord2.id_p == 2

    coord3 = CoordinadorDePracticas(id_p=-10, nombre_y_apellido="Ana Nuñez 3", cedula_dni="1798765433", correo_electronico="ana3@unl.edu.ec", direccion="Loja")
    assert repo.guardar(coord3) is True
    assert coord3.id_p == 3

    # Load and update
    repo2 = CoordinadorRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.nombre_y_apellido == "Ana Nuñez"

    loaded.nombre_y_apellido = "Ana Nuñez Updated"
    assert repo2.guardar(loaded) is True

    repo3 = CoordinadorRepository()
    assert repo3.buscar_por_id(1).nombre_y_apellido == "Ana Nuñez Updated"

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_empresa_repository():
    repo = EmpresaRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.obtener_todos() == []

    emp = Empresa(id_e=None, nombre_empresa="Tech Solutions S.A.", estado_de_convenio_emp=EstadoConvenio.VIGENTE, correo_electronico="info@tech.com")
    assert repo.guardar(emp) is True
    assert (TEST_DB_DIR / "empresas.dat").exists()
    assert emp.id_e == 1

    # Auto-increment
    emp2 = Empresa(id_e=0, nombre_empresa="Tech Solutions 2", estado_de_convenio_emp=EstadoConvenio.VIGENTE, correo_electronico="info2@tech.com")
    assert repo.guardar(emp2) is True
    assert emp2.id_e == 2

    emp3 = Empresa(id_e=-1, nombre_empresa="Tech Solutions 3", estado_de_convenio_emp=EstadoConvenio.VIGENTE, correo_electronico="info3@tech.com")
    assert repo.guardar(emp3) is True
    assert emp3.id_e == 3

    # Load and update
    repo2 = EmpresaRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.nombre_empresa == "Tech Solutions S.A."

    loaded.nombre_empresa = "Tech Solutions S.A. Updated"
    assert repo2.guardar(loaded) is True

    repo3 = EmpresaRepository()
    assert repo3.buscar_por_id(1).nombre_empresa == "Tech Solutions S.A. Updated"

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_estudiante_repository():
    repo = EstudianteRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.buscar_por_cedula("nonexistent") is None
    assert repo.buscar_persona_por_id(999) is None
    assert repo.obtener_todos() == []

    est = Estudiante(
        id_p=None,
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
    assert repo.guardar(est) is True
    assert (TEST_DB_DIR / "estudiantes.dat").exists()
    assert est.id_p == 1

    # Auto-increment
    est2 = Estudiante(
        id_p=0,
        nombre_y_apellido="Maria Lopez",
        cedula_dni="1712345679",
        correo_electronico="maria@unl.edu.ec",
        direccion="Loja Norte",
        ciclo_actual=7,
        estado_de_matricula=EstadoMatricula.MATRICULADO,
        malla_academica="malla.pdf",
        curriculum_vitae="cv.pdf",
        historial_practicas="Ninguno",
        estado_practica=EstadoPracticaEstudiante.SIN_PRACTICAS,
    )
    assert repo.guardar(est2) is True
    assert est2.id_p == 2

    est3 = Estudiante(
        id_p=-1,
        nombre_y_apellido="Carlos Perez",
        cedula_dni="1712345680",
        correo_electronico="carlos@unl.edu.ec",
        direccion="Loja Sur",
        ciclo_actual=5,
        estado_de_matricula=EstadoMatricula.MATRICULADO,
        malla_academica="malla.pdf",
        curriculum_vitae="cv.pdf",
        historial_practicas="Ninguno",
        estado_practica=EstadoPracticaEstudiante.SIN_PRACTICAS,
    )
    assert repo.guardar(est3) is True
    assert est3.id_p == 3

    # Load and update
    repo2 = EstudianteRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.nombre_y_apellido == "Juan Perez"

    loaded.nombre_y_apellido = "Juan Perez Updated"
    assert repo2.guardar(loaded) is True

    repo3 = EstudianteRepository()
    assert repo3.buscar_por_id(1).nombre_y_apellido == "Juan Perez Updated"

    # Specific searches
    assert repo3.buscar_por_cedula("1712345679").id_p == 2
    assert repo3.buscar_persona_por_id(2).nombre_y_apellido == "Maria Lopez"

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_formulario_repository():
    repo = FormularioRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.buscar_por_clave_compuesta(999, 999) is None
    assert repo.listar_formularios_por_practica(999) == []
    assert repo.obtener_todos() == []

    form = Formulario(
        id_doc=None,
        id_pr=200,
        tipo_formulario=TipoFormulario.FORMULARIO_1,
        estado_de_firma=EstadoFirmaFormulario.PRESENTADO,
        fecha_de_entrega_registro="2026-05-20",
        numero_formulario="FORM-001",
    )
    assert repo.guardar(form) is True
    assert (TEST_DB_DIR / "formularios.dat").exists()
    assert form.id_doc == 1

    # Auto-increment
    form2 = Formulario(
        id_doc=0,
        id_pr=200,
        tipo_formulario=TipoFormulario.FORMULARIO_2,
        estado_de_firma=EstadoFirmaFormulario.PRESENTADO,
        fecha_de_entrega_registro="2026-05-20",
        numero_formulario="FORM-002",
    )
    assert repo.guardar(form2) is True
    assert form2.id_doc == 2

    form3 = Formulario(
        id_doc=-1,
        id_pr=201,
        tipo_formulario=TipoFormulario.FORMULARIO_3,
        estado_de_firma=EstadoFirmaFormulario.PRESENTADO,
        fecha_de_entrega_registro="2026-05-20",
        numero_formulario="FORM-003",
    )
    assert repo.guardar(form3) is True
    assert form3.id_doc == 3

    # Load and update
    repo2 = FormularioRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.numero_formulario == "FORM-001"

    loaded.numero_formulario = "FORM-001-Updated"
    assert repo2.guardar(loaded) is True

    repo3 = FormularioRepository()
    assert repo3.buscar_por_id(1).numero_formulario == "FORM-001-Updated"

    # Specific searches
    assert repo3.buscar_por_clave_compuesta(2, 200).numero_formulario == "FORM-002"
    forms = repo3.listar_formularios_por_practica(200)
    assert len(forms) == 2

    # Delete
    assert repo3.eliminar((2, 200)) is True
    assert repo3.buscar_por_id(2) is None
    assert repo3.eliminar(3) is True
    assert repo3.buscar_por_id(3) is None


def test_oferta_repository():
    repo = OfertaRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.buscar_por_clave_compuesta(999, 999) is None
    assert repo.listar_por_empresa(999) == []
    assert repo.listar_todas() == []
    assert repo.listar_ofertas_disponibles() == []
    assert repo.obtener_todos() == []

    oferta = Oferta(
        id_o=None,
        id_e=10,
        descripcion_oferta="Desarrollador Python",
        requisitos="Python, Git",
        fecha_de_publicacion="2026-05-01",
        duracion="6 meses",
        remuneracion=400.0,
        validada_por_coordinador=True,
    )
    assert repo.guardar(oferta) is True
    assert (TEST_DB_DIR / "ofertas.dat").exists()
    assert oferta.id_o == 1

    # Auto-increment
    oferta2 = Oferta(
        id_o=0,
        id_e=10,
        descripcion_oferta="Desarrollador Java",
        requisitos="Java, Spring",
        fecha_de_publicacion="2026-05-01",
        duracion="6 meses",
        remuneracion=450.0,
        validada_por_coordinador=True,
    )
    assert repo.guardar(oferta2) is True
    assert oferta2.id_o == 2

    oferta3 = Oferta(
        id_o=-5,
        id_e=11,
        descripcion_oferta="Analista QA",
        requisitos="Testing, SQL",
        fecha_de_publicacion="2026-05-01",
        duracion="6 meses",
        remuneracion=350.0,
        validada_por_coordinador=True,
    )
    assert repo.guardar(oferta3) is True
    assert oferta3.id_o == 3

    # Load and update
    repo2 = OfertaRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.descripcion_oferta == "Desarrollador Python"

    loaded.descripcion_oferta = "Desarrollador Python Updated"
    assert repo2.guardar(loaded) is True

    repo3 = OfertaRepository()
    assert repo3.buscar_por_id(1).descripcion_oferta == "Desarrollador Python Updated"

    # Specific searches
    assert repo3.buscar_por_clave_compuesta(2, 10).descripcion_oferta == "Desarrollador Java"
    assert len(repo3.listar_por_empresa(10)) == 2
    assert len(repo3.listar_todas()) == 3
    assert len(repo3.listar_ofertas_disponibles()) == 3

    # Delete
    assert repo3.eliminar((2, 10)) is True
    assert repo3.buscar_por_id(2) is None
    assert repo3.eliminar(3) is True
    assert repo3.buscar_por_id(3) is None


def test_postulacion_repository():
    repo = PostulacionRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.listar_por_estudiante(999) == []
    assert repo.listar_por_oferta_compuesta("999", 999) == []
    assert repo.listar_por_id_terna(999) == []
    assert repo.obtener_todos() == []

    post = Postulacion(
        id_pos=None,
        id_p_estudiante=2,
        id_o=5,
        id_e=10,
        id_p_coordinador=4,
        fecha_postulacion="2026-05-01",
        estado_de_postulacion=EstadoPostulacion.PENDIENTE,
    )
    post.id_terna = 100
    assert repo.guardar(post) is True
    assert (TEST_DB_DIR / "postulaciones.dat").exists()
    assert post.id_pos == 1

    # Auto-increment
    post2 = Postulacion(
        id_pos=0,
        id_p_estudiante=2,
        id_o=6,
        id_e=10,
        id_p_coordinador=4,
        fecha_postulacion="2026-05-01",
        estado_de_postulacion=EstadoPostulacion.PENDIENTE,
    )
    post2.id_terna = 100
    assert repo.guardar(post2) is True
    assert post2.id_pos == 2

    post3 = Postulacion(
        id_pos=-2,
        id_p_estudiante=3,
        id_o=5,
        id_e=10,
        id_p_coordinador=4,
        fecha_postulacion="2026-05-01",
        estado_de_postulacion=EstadoPostulacion.PENDIENTE,
    )
    post3.id_terna = 101
    assert repo.guardar(post3) is True
    assert post3.id_pos == 3

    # Load and update
    repo2 = PostulacionRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.id_o == 5

    loaded.id_o = 99
    assert repo2.guardar(loaded) is True

    repo3 = PostulacionRepository()
    assert repo3.buscar_por_id(1).id_o == 99

    # Specific searches
    assert len(repo3.listar_por_estudiante(2)) == 2
    assert len(repo3.listar_por_oferta_compuesta(5, 10)) == 1
    assert len(repo3.listar_por_id_terna(100)) == 2

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_practica_repository():
    # Save a Postulacion first to test integration
    pos_repo = PostulacionRepository()
    post = Postulacion(
        id_pos=10,
        id_p_estudiante=22,
        id_o=5,
        id_e=10,
        id_p_coordinador=4,
        fecha_postulacion="2026-05-01",
        estado_de_postulacion=EstadoPostulacion.PENDIENTE,
    )
    pos_repo.guardar(post)

    repo = PracticaRepository()

    # Nonexistent file resilience
    assert repo.buscar_por_id(999) is None
    assert repo.buscar_practica_activa_estudiante(999) is None
    assert repo.obtener_todos() == []

    # Save
    prac = Practica(
        id_pr=None,
        id_pos=10,
        id_p_tutor_acad=5,
        id_p_tutor_emp=6,
        fecha_inicio="2026-05-15",
        fecha_fin="2026-11-15",
        estado_de_practica=EstadoPractica.INICIADA,
    )
    assert repo.guardar(prac) is True
    assert (TEST_DB_DIR / "practicas.dat").exists()
    assert prac.id_pr == 1

    # Auto-increment
    prac2 = Practica(
        id_pr=0,
        id_pos=11,
        id_p_tutor_acad=5,
        id_p_tutor_emp=6,
        fecha_inicio="2026-05-15",
        fecha_fin="2026-11-15",
        estado_de_practica=EstadoPractica.INICIADA,
    )
    assert repo.guardar(prac2) is True
    assert prac2.id_pr == 2

    prac3 = Practica(
        id_pr=-1,
        id_pos=12,
        id_p_tutor_acad=5,
        id_p_tutor_emp=6,
        fecha_inicio="2026-05-15",
        fecha_fin="2026-11-15",
        estado_de_practica=EstadoPractica.INICIADA,
    )
    assert repo.guardar(prac3) is True
    assert prac3.id_pr == 3

    # Load and update
    repo2 = PracticaRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.id_pos == 10

    loaded.estado_de_practica = EstadoPractica.FINALIZADA
    assert repo2.guardar(loaded) is True

    repo3 = PracticaRepository()
    assert repo3.buscar_por_id(1).estado_de_practica == EstadoPractica.FINALIZADA

    # Specific searches
    post2 = Postulacion(
        id_pos=20,
        id_p_estudiante=22,
        id_o=5,
        id_e=10,
        id_p_coordinador=4,
        fecha_postulacion="2026-05-01",
        estado_de_postulacion=EstadoPostulacion.PENDIENTE,
    )
    pos_repo.guardar(post2)

    prac4 = Practica(
        id_pr=None,
        id_pos=20,
        id_p_tutor_acad=5,
        id_p_tutor_emp=6,
        fecha_inicio="2026-05-15",
        fecha_fin="2026-11-15",
        estado_de_practica=EstadoPractica.INICIADA,
    )
    repo3.guardar(prac4)

    active_prac = repo3.buscar_practica_activa_estudiante(22)
    assert active_prac is not None
    assert active_prac.id_pos == 20
    assert repo3.buscar_por_estudiante(22).id_pos == 20

    # Delete
    assert repo3.eliminar(2) is True
    assert repo3.buscar_por_id(2) is None


def test_solicitud_autorizacion_repository():
    repo = SolicitudAutorizacionRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.listar_por_estudiante(999) == []
    assert repo.obtener_todos() == []

    sol = SolicitudAutorizacion(
        id_sol_aut=None,
        id_p_estudiante=2,
        nombre_empresa="Own Corp",
        detalles_empresa="Startup",
        fecha_solicitud="2026-05-10",
        estado_solicitud=EstadoSolicitudAutorizacion.PENDIENTE,
    )
    assert repo.guardar(sol) is True
    assert (TEST_DB_DIR / "solicitudes_autorizacion.dat").exists()
    assert sol.id_sol_aut == 1

    # Auto-increment
    sol2 = SolicitudAutorizacion(
        id_sol_aut=0,
        id_p_estudiante=2,
        nombre_empresa="Own Corp 2",
        detalles_empresa="Startup",
        fecha_solicitud="2026-05-10",
        estado_solicitud=EstadoSolicitudAutorizacion.PENDIENTE,
    )
    assert repo.guardar(sol2) is True
    assert sol2.id_sol_aut == 2

    sol3 = SolicitudAutorizacion(
        id_sol_aut=-100,
        id_p_estudiante=3,
        nombre_empresa="Own Corp 3",
        detalles_empresa="Startup",
        fecha_solicitud="2026-05-10",
        estado_solicitud=EstadoSolicitudAutorizacion.PENDIENTE,
    )
    assert repo.guardar(sol3) is True
    assert sol3.id_sol_aut == 3

    # Load and update
    repo2 = SolicitudAutorizacionRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.nombre_empresa == "Own Corp"

    loaded.nombre_empresa = "Own Corp Updated"
    assert repo2.guardar(loaded) is True

    repo3 = SolicitudAutorizacionRepository()
    assert repo3.buscar_por_id(1).nombre_empresa == "Own Corp Updated"

    # Specific searches
    assert len(repo3.listar_por_estudiante(2)) == 2

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_solicitud_oficio_repository():
    repo = SolicitudOficioRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.listar_por_estudiante(999) == []
    assert repo.obtener_todos() == []

    sol = SolicitudOficio(
        id_sol_of=None,
        id_p_estudiante=2,
        nombre_destinatario="Gerente",
        cargo_destinatario="CEO",
        nombre_empresa="Own Corp",
        fecha_solicitud="2026-05-10",
        estado_solicitud=EstadoSolicitudOficio.PENDIENTE,
    )
    assert repo.guardar(sol) is True
    assert (TEST_DB_DIR / "solicitudes_oficio.dat").exists()
    assert sol.id_sol_of == 1

    # Auto-increment
    sol2 = SolicitudOficio(
        id_sol_of=0,
        id_p_estudiante=2,
        nombre_destinatario="Gerente 2",
        cargo_destinatario="CEO",
        nombre_empresa="Own Corp 2",
        fecha_solicitud="2026-05-10",
        estado_solicitud=EstadoSolicitudOficio.PENDIENTE,
    )
    assert repo.guardar(sol2) is True
    assert sol2.id_sol_of == 2

    sol3 = SolicitudOficio(
        id_sol_of=-5,
        id_p_estudiante=3,
        nombre_destinatario="Gerente 3",
        cargo_destinatario="CEO",
        nombre_empresa="Own Corp 3",
        fecha_solicitud="2026-05-10",
        estado_solicitud=EstadoSolicitudOficio.PENDIENTE,
    )
    assert repo.guardar(sol3) is True
    assert sol3.id_sol_of == 3

    # Load and update
    repo2 = SolicitudOficioRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.nombre_destinatario == "Gerente"

    loaded.nombre_destinatario = "Gerente Updated"
    assert repo2.guardar(loaded) is True

    repo3 = SolicitudOficioRepository()
    assert repo3.buscar_por_id(1).nombre_destinatario == "Gerente Updated"

    # Specific searches
    assert len(repo3.listar_por_estudiante(2)) == 2

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_tutor_academico_repository():
    repo = TutorAcademicoRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.obtener_todos() == []

    tutor = TutorAcademico(
        id_p=None,
        nombre_y_apellido="Carlos Mendoza",
        cedula_dni="1723456789",
        correo_electronico="carlos@unl.edu.ec",
        direccion="Loja",
    )
    assert repo.guardar(tutor) is True
    assert (TEST_DB_DIR / "tutores_academicos.dat").exists()
    assert tutor.id_p == 1

    # Auto-increment
    tutor2 = TutorAcademico(
        id_p=0,
        nombre_y_apellido="Carlos Mendoza 2",
        cedula_dni="1723456790",
        correo_electronico="carlos2@unl.edu.ec",
        direccion="Loja",
    )
    assert repo.guardar(tutor2) is True
    assert tutor2.id_p == 2

    tutor3 = TutorAcademico(
        id_p=-1,
        nombre_y_apellido="Carlos Mendoza 3",
        cedula_dni="1723456791",
        correo_electronico="carlos3@unl.edu.ec",
        direccion="Loja",
    )
    assert repo.guardar(tutor3) is True
    assert tutor3.id_p == 3

    # Load and update
    repo2 = TutorAcademicoRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.nombre_y_apellido == "Carlos Mendoza"

    loaded.nombre_y_apellido = "Carlos Mendoza Updated"
    assert repo2.guardar(loaded) is True

    repo3 = TutorAcademicoRepository()
    assert repo3.buscar_por_id(1).nombre_y_apellido == "Carlos Mendoza Updated"

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_tutor_empresarial_repository():
    repo = TutorEmpresarialRepository()

    assert repo.buscar_por_id(999) is None
    assert repo.listar_por_empresa(999) == []
    assert repo.obtener_todos() == []

    tutor = TutorEmpresarial(
        id_p=None,
        nombre_y_apellido="Luis Gomez",
        cedula_dni="1734567890",
        correo_electronico="luis@solutions.com",
        direccion="Quito",
        id_e=10,
    )
    assert repo.guardar(tutor) is True
    assert (TEST_DB_DIR / "tutores_empresariales.dat").exists()
    assert tutor.id_p == 1

    # Auto-increment
    tutor2 = TutorEmpresarial(
        id_p=0,
        nombre_y_apellido="Luis Gomez 2",
        cedula_dni="1734567891",
        correo_electronico="luis2@solutions.com",
        direccion="Quito",
        id_e=10,
    )
    assert repo.guardar(tutor2) is True
    assert tutor2.id_p == 2

    tutor3 = TutorEmpresarial(
        id_p=-100,
        nombre_y_apellido="Luis Gomez 3",
        cedula_dni="1734567892",
        correo_electronico="luis3@solutions.com",
        direccion="Quito",
        id_e=11,
    )
    assert repo.guardar(tutor3) is True
    assert tutor3.id_p == 3

    # Load and update
    repo2 = TutorEmpresarialRepository()
    loaded = repo2.buscar_por_id(1)
    assert loaded is not None
    assert loaded.nombre_y_apellido == "Luis Gomez"

    loaded.nombre_y_apellido = "Luis Gomez Updated"
    assert repo2.guardar(loaded) is True

    repo3 = TutorEmpresarialRepository()
    assert repo3.buscar_por_id(1).nombre_y_apellido == "Luis Gomez Updated"

    # Specific searches
    assert len(repo3.listar_por_empresa(10)) == 2

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_id(1) is None


def test_usuario_repository():
    repo = UsuarioRepository()

    assert repo.buscar_por_username("nonexistent") is None
    assert repo.obtener_todos() == []

    u = Usuario(
        id_u=None,
        username_correo="sofia@unl.edu.ec",
        contrasena="pass123",
        rol=RolUsuario.ADMINISTRADOR,
        id_p=7,
    )
    assert repo.guardar(u) is True
    assert (TEST_DB_DIR / "usuarios.dat").exists()
    assert u.id_u == 1

    # Auto-increment
    u2 = Usuario(
        id_u=0,
        username_correo="maria@unl.edu.ec",
        contrasena="pass123",
        rol=RolUsuario.ESTUDIANTE,
        id_p=8,
    )
    assert repo.guardar(u2) is True
    assert u2.id_u == 2

    u3 = Usuario(
        id_u=-5,
        username_correo="carlos@unl.edu.ec",
        contrasena="pass123",
        rol=RolUsuario.ESTUDIANTE,
        id_p=9,
    )
    assert repo.guardar(u3) is True
    assert u3.id_u == 3

    # Load and update
    repo2 = UsuarioRepository()
    loaded = repo2.buscar_por_username("sofia@unl.edu.ec")
    assert loaded is not None
    assert loaded.contrasena == "pass123"

    loaded.contrasena = "newpass"
    assert repo2.guardar(loaded) is True

    repo3 = UsuarioRepository()
    assert repo3.buscar_por_username("sofia@unl.edu.ec").contrasena == "newpass"

    # Delete
    assert repo3.eliminar(1) is True
    assert repo3.buscar_por_username("sofia@unl.edu.ec") is None
