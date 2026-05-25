from pathlib import Path
from typing import Optional

from src.models import Convenio
from src.repositories.interfaces.convenio_repository_abc import ConvenioRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class ConvenioRepository(ConvenioRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/convenios.dat")
        self._datos: list[Convenio] = []

    def _cargar_datos(self) -> None:
        if self.filepath.exists():
            self._datos = load_db_dat(self.filepath)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: Convenio) -> bool:
        self._cargar_datos()

        if entidad.id_con is None or entidad.id_con <= 0:
            current_ids = [c.id_con for c in self._datos]
            entidad.id_con = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, c in enumerate(self._datos):
                if c.id_con == entidad.id_con:
                    self._datos[idx] = entidad
                    break
            else:
                return False

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [c for c in self._datos if c.id_con != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_con: int) -> Optional[Convenio]:
        self._cargar_datos()
        for c in self._datos:
            if c.id_con == id_con:
                return c
        return None

    def buscar_por_empresa(self, id_e: int) -> Optional[Convenio]:
        self._cargar_datos()
        for c in self._datos:
            if c.id_e == id_e:
                return c
        return None
