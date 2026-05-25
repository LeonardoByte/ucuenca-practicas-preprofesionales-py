import pickle
from pathlib import Path
from typing import Any, List

from src.models import (
    Estudiante,
    CoordinadorDePracticas,
    TutorAcademico,
    TutorEmpresarial,
    Empresa,
    Usuario,
)


def inicializar_semilla(filepath: Path) -> List[Any]:
    # Usamos match-case sobre el nombre del archivo para mayor limpieza visual
    match filepath.name:
        case "usuarios.dat":
            return [
                Usuario(id_u=1, username_correo="estudiante1@unl.edu.ec", contrasena="pass123", rol="Estudiante", id_p=1),
                Usuario(id_u=2, username_correo="coordinador1@unl.edu.ec", contrasena="pass123", rol="Coordinador", id_p=2),
                Usuario(id_u=3, username_correo="tutoracad1@unl.edu.ec", contrasena="pass123", rol="Tutor Academico", id_p=3),
                Usuario(id_u=4, username_correo="tutoremp1@unl.edu.ec", contrasena="pass123", rol="Tutor Empresarial", id_p=4),
                Usuario(id_u=5, username_correo="empresa1@unl.edu.ec", contrasena="pass123", rol="Empresa", id_p=10),
            ]
        case "estudiantes.dat":
            return [
                Estudiante(
                    id_p=1,
                    nombre_y_apellido="Juan Perez",
                    cedula_dni="1712345678",
                    correo_electronico="juan.perez@unl.edu.ec",
                    direccion="Av. Universitaria, Loja",
                    ciclo_actual="6",
                    estado_de_matricula="Matriculado",
                    malla_academica="storage/documents/malla_juan.pdf",
                    curriculum_vitae="storage/documents/cv_juan.pdf",
                    historial_practicas="Ninguno",
                    estado_practica="Sin Practicas",
                )
            ]
        case "coordinadores.dat":
            return [
                CoordinadorDePracticas(
                    id_p=2,
                    nombre_y_apellido="Dra. Ana Gabriela Nuñez",
                    cedula_dni="1798765432",
                    correo_electronico="ana.nunez@unl.edu.ec",
                    direccion="Av. Reinaldo Espinosa, Loja",
                )
            ]
        case "tutores_academicos.dat":
            return [
                TutorAcademico(
                    id_p=3,
                    nombre_y_apellido="Ing. Carlos Mendoza",
                    cedula_dni="1723456789",
                    correo_electronico="carlos.mendoza@unl.edu.ec",
                    direccion="Loja Centro",
                )
            ]
        case "tutores_empresariales.dat":
            return [
                TutorEmpresarial(
                    id_p=4,
                    nombre_y_apellido="Ing. Luis Gomez",
                    cedula_dni="1734567890",
                    correo_electronico="luis.gomez@techsolutions.com",
                    direccion="Quito Norte",
                    id_e=10,
                )
            ]
        case "empresas.dat":
            return [
                Empresa(id_e=10, nombre_empresa="Tech Solutions S.A.", estado_de_convenio_emp="Vigente")
            ]
        case _:
            return []


def load_db_dat(filepath: Path) -> Any:
    """Carga los datos binarios serializados con Pickle."""
    if not filepath.exists():
        data = inicializar_semilla(filepath)
        if data:
            save_db_dat(filepath, data)
            return data
        return []

    with open(filepath, "rb") as f:
        try:
            return pickle.load(f)
        except (pickle.UnpicklingError, EOFError):
            return []


def save_db_dat(filepath: Path, data: Any) -> None:
    """Guarda los datos en formato binario .dat usando Pickle."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "wb") as f:
        pickle.dump(data, f)
