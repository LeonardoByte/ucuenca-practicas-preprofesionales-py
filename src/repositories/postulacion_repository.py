from pathlib import Path
from typing import Optional

from src.models import Postulacion
from src.repositories.interfaces.postulacion_repository_abc import PostulacionRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class PostulacionRepository(PostulacionRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/postulaciones.dat")
        self._datos: list[Postulacion] = []

    def _cargar_datos(self) -> None:
        if self.filepath.exists():
            self._datos = load_db_dat(self.filepath)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: Postulacion) -> bool:
        self._cargar_datos()

        if entidad.id_pos is None or entidad.id_pos <= 0:
            current_ids = [p.id_pos for p in self._datos]
            entidad.id_pos = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, p in enumerate(self._datos):
                if p.id_pos == entidad.id_pos:
                    self._datos[idx] = entidad
                    break
            else:
                return False

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [p for p in self._datos if p.id_pos != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_pos: int) -> Optional[Postulacion]:
        self._cargar_datos()
        for p in self._datos:
            if p.id_pos == id_pos:
                return p
        return None

    def listar_por_estudiante(self, id_p_estudiante: int) -> list[Postulacion]:
        self._cargar_datos()
        return [p for p in self._datos if p.id_p_estudiante == id_p_estudiante]

    def listar_por_oferta_compuesta(self, id_o: str, id_e: int) -> list[Postulacion]:
        self._cargar_datos()
        return [p for p in self._datos if p.id_o == id_o and p.id_e == id_e]

    def listar_por_id_terna(self, id_terna: int) -> list[Postulacion]:
        self._cargar_datos()
        return [p for p in self._datos if p.id_terna == id_terna]
