"""
Módulo 0: Tests de Infraestructura y Entorno Base

Audita el entorno de desarrollo validando:
- Existencia de directorios según MVC + Services + Repo
- Presencia de archivos .dat semilla (NO .json)
- Disponibilidad de dependencias (PyQt6, pytest, pytest-qt, ruff)
- Aislamiento de Git (.git/ e .gitignore)
"""

import importlib.util
import pathlib
import shutil


def test_directory_existence():
    """Verifica que todas las carpetas clave del workspace existan físicamente."""
    base_dir = pathlib.Path(__file__).parent.parent.parent

    required_directories = [
        "src",
        "src/views",
        "src/controllers",
        "src/models",
        "src/services",
        "src/repositories",
        "storage",
        "storage/db",
        "storage/documents",
        "tests",
        "tests/unit",
        "tests/integration",
    ]

    for relative_path in required_directories:
        directory_path = base_dir / relative_path
        assert directory_path.exists(), f"Directory '{relative_path}' does not exist."
        assert directory_path.is_dir(), f"'{relative_path}' is not a directory."


def test_seed_files_existence():
    """Valida que los ficheros binarios .dat existan en storage/db/ y no haya .json."""
    base_dir = pathlib.Path(__file__).parent.parent.parent

    required_seeds = [
        "storage/db/usuarios.dat",
        "storage/db/administradores.dat",
        "storage/db/estudiantes.dat",
        "storage/db/coordinadores.dat",
        "storage/db/tutores_academicos.dat",
        "storage/db/tutores_empresariales.dat",
        "storage/db/empresas.dat",
    ]

    for relative_path in required_seeds:
        file_path = base_dir / relative_path
        assert file_path.exists(), f"Seed file '{relative_path}' does not exist."
        assert file_path.is_file(), f"'{relative_path}' is not a file."
        assert file_path.stat().st_size > 0, f"Seed file '{relative_path}' is empty."

    json_files = list((base_dir / "storage" / "db").glob("*.json"))
    assert len(json_files) == 0, (
        f"Found JSON files in storage/db/ (prohibited): {json_files}. "
        "Only .dat binary files are allowed per specification."
    )


def test_dependency_availability():
    """Valida que PyQt6, pytest, pytest-qt y ruff estén accesibles."""
    dependencies = ["PyQt6", "pytest", "pytestqt"]
    for dep in dependencies:
        spec = importlib.util.find_spec(dep)
        assert spec is not None, f"Dependency '{dep}' is not available in the environment."

    base_dir = pathlib.Path(__file__).parent.parent.parent
    venv_bin = base_dir / ".venv" / "Scripts"

    if venv_bin.exists():
        ruff_exe = venv_bin / "ruff.exe"
        if ruff_exe.exists():
            return

    assert shutil.which("ruff") is not None, "ruff executable not found in PATH or .venv/Scripts"


def test_git_isolation():
    """Verifica que .git/ esté inicializado y .gitignore esté configurado."""
    base_dir = pathlib.Path(__file__).parent.parent.parent

    git_dir = base_dir / ".git"
    assert git_dir.exists(), ".git/ directory was not found. Git is not initialized."
    assert git_dir.is_dir(), ".git/ is not a directory."

    gitignore_file = base_dir / ".gitignore"
    assert gitignore_file.exists(), ".gitignore file does not exist."

    with open(gitignore_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "storage/documents/*" in content, (
        "storage/documents/ files are not being ignored in .gitignore"
    )
    assert "!storage/documents/.gitkeep" in content, (
        "storage/documents/.gitkeep is not exempt from gitignore"
    )
