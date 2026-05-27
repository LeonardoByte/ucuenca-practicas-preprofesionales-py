"""
Módulo de inicialización de datos semilla para la base de datos.

Genera archivos binarios .dat con pickle para los datos semilla del sistema.
Todos los archivos comienzan sus secuencias numéricas correlativas de ID en 1.
"""

from pathlib import Path
import pickle
from src.models import (
    Usuario, Administrador, Estudiante, 
    CoordinadorDePracticas, TutorAcademico, 
    TutorEmpresarial, Empresa
)


def inicializar_todos_los_dat_semilla():
    """
    Genera físicamente la estructura de datos semilla en archivos binarios .dat
    dentro de storage/db/, garantizando que todos los repositorios arranquen
    con sus identificadores primarios en 1.
    """
    base_path = Path("storage/db")
    base_path.mkdir(parents=True, exist_ok=True)
    
    semillas = {
        "usuarios.dat": [
            Usuario(id_u=1, username_correo="sofia.ramirez@unl.edu.ec", contrasena="pass123", rol="Administrador", id_p=1),
            Usuario(id_u=2, username_correo="juan.perez@unl.edu.ec", contrasena="pass123", rol="Estudiante", id_p=1),
            Usuario(id_u=3, username_correo="ana.nunez@unl.edu.ec", contrasena="pass123", rol="Coordinador", id_p=1),
            Usuario(id_u=4, username_correo="carlos.mendoza@unl.edu.ec", contrasena="pass123", rol="Tutor Academico", id_p=1),
            Usuario(id_u=5, username_correo="tutoremp1@unl.edu.ec", contrasena="pass123", rol="Tutor Empresarial", id_p=1),
            Usuario(id_u=6, username_correo="info@techsolutions.com", contrasena="pass123", rol="Empresa", id_p=1),
        ],
        "administradores.dat": [
            Administrador(
                id_p=1,
                nombre_y_apellido="Ing. Sofia Ramirez",
                cedula_dni="1745678901",
                correo_electronico="sofia.ramirez@unl.edu.ec",
                direccion="Av. Reinaldo Espinosa, Loja"
            )
        ],
        "estudiantes.dat": [
            Estudiante(
                id_p=1,
                nombre_y_apellido="Juan Perez",
                cedula_dni="1712345678",
                correo_electronico="juan.perez@unl.edu.ec",
                direccion="Av. Universitaria, Loja",
                ciclo_actual=6,
                estado_de_matricula="Matriculado",
                malla_academica="storage/documents/malla_juan.pdf",
                curriculum_vitae="storage/documents/cv_juan.pdf",
                historial_practicas="Ninguno",
                estado_practica="Sin Practicas"
            )
        ],
        "coordinadores.dat": [
            CoordinadorDePracticas(
                id_p=1,
                nombre_y_apellido="Dra. Ana Gabriela Nuñez",
                cedula_dni="1798765432",
                correo_electronico="ana.nunez@unl.edu.ec",
                direccion="Av. Reinaldo Espinosa, Loja"
            )
        ],
        "tutores_academicos.dat": [
            TutorAcademico(
                id_p=1,
                nombre_y_apellido="Ing. Carlos Mendoza",
                cedula_dni="1723456789",
                correo_electronico="carlos.mendoza@unl.edu.ec",
                direccion="Loja Centro"
            )
        ],
        "tutores_empresariales.dat": [
            TutorEmpresarial(
                id_p=1,
                nombre_y_apellido="Ing. Luis Gomez",
                cedula_dni="1734567890",
                correo_electronico="luis.gomez@techsolutions.com",
                direccion="Quito Norte",
                id_e=1
            )
        ],
        "empresas.dat": [
            Empresa(
                id_e=1,
                nombre_empresa="Tech Solutions S.A.",
                estado_de_convenio_emp="Vigente",
                correo_electronico="info@techsolutions.com"
            )
        ]
    }
    
    for filename, datos in semillas.items():
        file_key = base_path / filename
        with open(file_key, "wb") as f:
            pickle.dump(datos, f)
        print(f"✓ Creado: {file_key}")
