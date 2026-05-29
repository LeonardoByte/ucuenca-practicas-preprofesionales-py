from pathlib import Path
from typing import Optional

from src.models import CoordinadorDePracticas
from src.repositories.interfaces.coordinador_repository_abc import CoordinadorRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class CoordinadorRepository(CoordinadorRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/coordinadores.dat")
        self._datos: list[CoordinadorDePracticas] = []

    def _cargar_datos(self) -> None:
        self._datos = load_db_dat(self.filepath)

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: CoordinadorDePracticas) -> bool:
        self._cargar_datos()

        if entidad.id_p is None or entidad.id_p <= 0:
            current_ids = [c.id_p for c in self._datos]
            entidad.id_p = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, c in enumerate(self._datos):
                if c.id_p == entidad.id_p:
                    self._datos[idx] = entidad
                    break
            else:
                return False

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [c for c in self._datos if c.id_p != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_p: int) -> Optional[CoordinadorDePracticas]:
        self._cargar_datos()
        for c in self._datos:
            if c.id_p == id_p:
                return c
        return None

    def obtener_todos(self) -> list[CoordinadorDePracticas]:
        self._cargar_datos()
        return list(self._datos)
