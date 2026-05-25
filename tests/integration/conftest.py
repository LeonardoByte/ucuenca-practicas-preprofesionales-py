import json
import pathlib
import shutil

import pytest


@pytest.fixture
def entorno_binario_temporal(tmp_path, monkeypatch):
    """Fixture that configures an ephemeral binary environment.

    Copies the seed JSON files to a temporary storage/db directory and changes
    the working directory so that repositories save files in this temporary directory.
    """
    # Create the directory structure in tmp_path
    db_dir = tmp_path / "storage" / "db"
    db_dir.mkdir(parents=True)

    # Find the original seed files relative to the project root
    project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    original_db_dir = project_root / "storage" / "db"

    # Copy json seed files
    for filename in ["usuarios.json", "personas.json", "empresas.json"]:
        src_file = original_db_dir / filename
        if src_file.exists():
            shutil.copy(src_file, db_dir / filename)
        else:
            # Fallback in case they are missing, create basic seed structure
            dummy_content = []
            if filename == "usuarios.json":
                dummy_content = [
                    {
                        "usuario": "estudiante1",
                        "contrasena": "pass123",
                        "rol": "Estudiante",
                        "id_p": 1,
                    },
                    {
                        "usuario": "coordinador1",
                        "contrasena": "pass123",
                        "rol": "Coordinador",
                        "id_p": 2,
                    },
                    {
                        "usuario": "tutoracad1",
                        "contrasena": "pass123",
                        "rol": "Tutor Academico",
                        "id_p": 3,
                    },
                    {
                        "usuario": "tutoremp1",
                        "contrasena": "pass123",
                        "rol": "Tutor Empresarial",
                        "id_p": 4,
                    },
                    {
                        "usuario": "empresa1",
                        "contrasena": "pass123",
                        "rol": "Empresa",
                        "id_e": 10,
                    },
                ]
            elif filename == "personas.json":
                dummy_content = [
                    {
                        "id_p": 1,
                        "nombre_y_apellido": "Juan Perez",
                        "cedula_dni": "1712345678",
                        "correo_electronico": "juan.perez@unl.edu.ec",
                        "direccion": "Av. Universitaria, Loja",
                        "rol": "Estudiante",
                        "ciclo_actual": "6",
                        "estado_de_matricula": "Matriculado",
                        "malla_academica": "storage/documents/malla_juan.pdf",
                        "curriculum_vitae": "storage/documents/cv_juan.pdf",
                        "historial_practicas": "Ninguno",
                        "estado_practica": "Sin Practicas",
                    },
                    {
                        "id_p": 2,
                        "nombre_y_apellido": "Dra. Ana Gabriela Nuñez",
                        "cedula_dni": "1798765432",
                        "correo_electronico": "ana.nunez@unl.edu.ec",
                        "direccion": "Av. Reinaldo Espinosa, Loja",
                        "rol": "Personal",
                        "rol_personal": "Coordinador",
                    },
                    {
                        "id_p": 3,
                        "nombre_y_apellido": "Ing. Carlos Mendoza",
                        "cedula_dni": "1723456789",
                        "correo_electronico": "carlos.mendoza@unl.edu.ec",
                        "direccion": "Loja Centro",
                        "rol": "Personal",
                        "rol_personal": "Tutor Academico",
                    },
                    {
                        "id_p": 4,
                        "nombre_y_apellido": "Ing. Luis Gomez",
                        "cedula_dni": "1734567890",
                        "correo_electronico": "luis.gomez@techsolutions.com",
                        "direccion": "Quito Norte",
                        "rol": "Personal",
                        "rol_personal": "Tutor Empresarial",
                        "id_e": 10,
                    },
                ]
            elif filename == "empresas.json":
                dummy_content = [
                    {
                        "id_e": 10,
                        "nombre_empresa": "Tech Solutions S.A.",
                        "estado_de_convenio_emp": "Vigente",
                    },
                    {
                        "id_e": 11,
                        "nombre_empresa": "Innovatech Corp",
                        "estado_de_convenio_emp": "No Vigente",
                    },
                ]
            with open(db_dir / filename, "w", encoding="utf-8") as f:
                json.dump(dummy_content, f, indent=2)

    # Change current working directory to the temporary path
    monkeypatch.chdir(tmp_path)

    return db_dir


@pytest.fixture
def estudiante_repo(entorno_binario_temporal):
    from src.repositories import EstudianteRepository
    return EstudianteRepository()


@pytest.fixture
def oferta_repo(entorno_binario_temporal):
    from src.repositories import OfertaRepository
    return OfertaRepository()


@pytest.fixture
def postulacion_repo(entorno_binario_temporal):
    from src.repositories import PostulacionRepository
    return PostulacionRepository()


@pytest.fixture
def practica_repo(entorno_binario_temporal):
    from src.repositories import PracticaRepository
    return PracticaRepository()


@pytest.fixture
def formulario_repo(entorno_binario_temporal):
    from src.repositories import FormularioRepository
    return FormularioRepository()


@pytest.fixture
def solicitud_autorizacion_repo(entorno_binario_temporal):
    from src.repositories import SolicitudAutorizacionRepository
    return SolicitudAutorizacionRepository()


@pytest.fixture
def solicitud_oficio_repo(entorno_binario_temporal):
    from src.repositories import SolicitudOficioRepository
    return SolicitudOficioRepository()


@pytest.fixture
def carta_compromiso_repo(entorno_binario_temporal):
    from src.repositories import CartaCompromisoRepository
    return CartaCompromisoRepository()


@pytest.fixture
def empresa_repo(entorno_binario_temporal):
    from src.repositories import EmpresaRepository
    return EmpresaRepository()


@pytest.fixture
def estudiante_service(
    estudiante_repo, oferta_repo, solicitud_autorizacion_repo, solicitud_oficio_repo
):
    from src.services import EstudianteService
    return EstudianteService(
        estudiante_repo=estudiante_repo,
        oferta_repo=oferta_repo,
        solicitud_autorizacion_repo=solicitud_autorizacion_repo,
        solicitud_oficio_repo=solicitud_oficio_repo,
    )


@pytest.fixture
def postulacion_service(postulacion_repo, estudiante_repo, practica_repo, oferta_repo):
    from src.services import PostulacionService
    return PostulacionService(
        postulacion_repo=postulacion_repo,
        estudiante_repo=estudiante_repo,
        practica_repo=practica_repo,
        oferta_repo=oferta_repo,
    )


@pytest.fixture
def practica_service(
    practica_repo,
    postulacion_repo,
    formulario_repo,
    carta_compromiso_repo,
    estudiante_repo,
    empresa_repo,
    oferta_repo,
    solicitud_autorizacion_repo,
):
    from src.services import PracticaService
    return PracticaService(
        practica_repo=practica_repo,
        postulacion_repo=postulacion_repo,
        formulario_repo=formulario_repo,
        carta_compromiso_repo=carta_compromiso_repo,
        estudiante_repo=estudiante_repo,
        empresa_repo=empresa_repo,
        oferta_repo=oferta_repo,
        solicitud_autorizacion_repo=solicitud_autorizacion_repo,
    )
