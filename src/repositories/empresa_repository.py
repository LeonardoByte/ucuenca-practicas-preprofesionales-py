from pathlib import Path
from typing import Optional

from src.models import Empresa
from src.repositories.interfaces.empresa_repository_abc import EmpresaRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class EmpresaRepository(EmpresaRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/empresas.dat")
        self._datos: list[Empresa] = []

    def _cargar_datos(self) -> None:
        self._datos = load_db_dat(self.filepath)

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: Empresa) -> bool:
        self._cargar_datos()

        if entidad.id_e is None or entidad.id_e <= 0:
            current_ids = [e.id_e for e in self._datos]
            entidad.id_e = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, e in enumerate(self._datos):
                if e.id_e == entidad.id_e:
                    self._datos[idx] = entidad
                    break
            else:
                self._datos.append(entidad)

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [e for e in self._datos if e.id_e != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_e: int) -> Optional[Empresa]:
        self._cargar_datos()
        for e in self._datos:
            if e.id_e == id_e:
                return e
        return None
