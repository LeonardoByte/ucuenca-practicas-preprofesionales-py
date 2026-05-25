from pathlib import Path
from typing import Optional

from src.models import Actividad
from src.repositories.interfaces import ActividadRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class ActividadRepository(ActividadRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/actividades.dat")
        self._datos: list[Actividad] = []

    def _cargar_datos(self) -> None:
        if self.filepath.exists():
            self._datos = load_db_dat(self.filepath)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: Actividad) -> bool:
        self._cargar_datos()

        if entidad.id_act is None or entidad.id_act <= 0:
            current_ids = [a.id_act for a in self._datos]
            entidad.id_act = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, a in enumerate(self._datos):
                if a.id_act == entidad.id_act and a.id_pr == entidad.id_pr:
                    self._datos[idx] = entidad
                    break
            else:
                return False

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [a for a in self._datos if a.id_act != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_act: int) -> Optional[Actividad]:
        self._cargar_datos()
        for a in self._datos:
            if a.id_act == id_act:
                return a
        return None

    def listar_por_practica(self, id_pr: int) -> list[Actividad]:
        self._cargar_datos()
        return [a for a in self._datos if a.id_pr == id_pr]
