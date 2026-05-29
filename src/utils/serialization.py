import pickle
from pathlib import Path
from typing import Any


def load_db_dat(filepath: Path) -> list[Any]:
    """Carga una lista de objetos desde un archivo binario .dat.

    Si el archivo no existe o ocurre algún error, retorna una lista vacía.
    """
    if not filepath.exists():
        return []
    try:
        with open(filepath, "rb") as f:
            return pickle.load(f)
    except Exception:
        return []


def save_db_dat(filepath: Path, datos: list[Any]) -> None:
    """Persiste una lista de objetos en un archivo binario .dat.

    Si el directorio de destino no existe, lo crea automáticamente.
    """
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(datos, f)
    except Exception:
        pass
