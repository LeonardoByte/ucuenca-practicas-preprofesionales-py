from pathlib import Path
from typing import Optional

from src.models import Administrador, Persona
from src.repositories.interfaces.administrador_repository_abc import AdministradorRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class AdministradorRepository(AdministradorRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/administradores.dat")
        self._datos: list[Administrador] = []

    def _cargar_datos(self) -> None:
        self._datos = load_db_dat(self.filepath)

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: Administrador) -> bool:
        self._cargar_datos()

        if entidad.id_p is None or entidad.id_p <= 0:
            current_ids = [p.id_p for p in self._datos]
            entidad.id_p = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, p in enumerate(self._datos):
                if p.id_p == entidad.id_p:
                    self._datos[idx] = entidad
                    break
            else:
                # Si no se encuentra para actualizar, se respeta la cláusula de tu bucle
                self._datos.append(entidad)

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [p for p in self._datos if p.id_p != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_p: int) -> Optional[Administrador]:
        self._cargar_datos()
        for p in self._datos:
            if p.id_p == id_p and isinstance(p, Administrador):
                return p
        return None

    def buscar_persona_por_id(self, id_p: int) -> Optional[Persona]:
        self._cargar_datos()
        for p in self._datos:
            if p.id_p == id_p:
                return p
        return None