from pathlib import Path
from typing import Optional

from src.models import TutorEmpresarial
from src.repositories.interfaces.tutor_empresarial_repository_abc import TutorEmpresarialRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class TutorEmpresarialRepository(TutorEmpresarialRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/tutores_empresariales.dat")
        self._datos: list[TutorEmpresarial] = []

    def _cargar_datos(self) -> None:
        self._datos = load_db_dat(self.filepath)

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: TutorEmpresarial) -> bool:
        self._cargar_datos()

        if entidad.id_p is None or entidad.id_p <= 0:
            current_ids = [t.id_p for t in self._datos]
            entidad.id_p = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, t in enumerate(self._datos):
                if t.id_p == entidad.id_p:
                    self._datos[idx] = entidad
                    break
            else:
                return False

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [t for t in self._datos if t.id_p != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_p: int) -> Optional[TutorEmpresarial]:
        self._cargar_datos()
        for t in self._datos:
            if t.id_p == id_p:
                return t
        return None

    def listar_por_empresa(self, id_e: int) -> list[TutorEmpresarial]:
        self._cargar_datos()
        return [t for t in self._datos if t.id_e == id_e]
