import importlib.util
import pathlib
import shutil


def test_directory_existence():
    """Verify that all key directories in the project workspace exist."""
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
    """Verify that the required database seed files exist in storage/db."""
    base_dir = pathlib.Path(__file__).parent.parent.parent

    required_seeds = [
        "storage/db/usuarios.json",
        "storage/db/personas.json",
        "storage/db/empresas.json",
    ]

    for relative_path in required_seeds:
        file_path = base_dir / relative_path
        assert file_path.exists(), f"Seed file '{relative_path}' does not exist."
        assert file_path.is_file(), f"'{relative_path}' is not a file."
        assert file_path.stat().st_size > 0, f"Seed file '{relative_path}' is empty."

def test_dependency_availability():
    """Verify that production and development libraries are importable and accessible."""
    dependencies = ["PyQt6", "pytest", "pytestqt"]
    for dep in dependencies:
        spec = importlib.util.find_spec(dep)
        assert spec is not None, f"Dependency '{dep}' is not available in the environment."

    # Check ruff executable availability
    base_dir = pathlib.Path(__file__).parent.parent.parent
    venv_bin = base_dir / ".venv" / "Scripts"
    ruff_exe = venv_bin / "ruff.exe"
    if not ruff_exe.exists():
        assert shutil.which("ruff") is not None, (
            "ruff executable not found in PATH or .venv/Scripts"
        )

def test_git_isolation():
    """Verify git is initialized and gitignore is properly configured."""
    base_dir = pathlib.Path(__file__).parent.parent.parent

    # Check git folder
    git_dir = base_dir / ".git"
    assert git_dir.exists(), ".git/ directory was not found. Git is not initialized."
    assert git_dir.is_dir(), ".git/ is not a directory."

    # Check gitignore rules
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
