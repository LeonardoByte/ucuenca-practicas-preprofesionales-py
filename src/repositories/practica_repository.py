from pathlib import Path
from typing import Optional

from src.models import Practica
from src.repositories.interfaces.practica_repository_abc import PracticaRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class PracticaRepository(PracticaRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/practicas.dat")
        self._datos: list[Practica] = []

    def _cargar_datos(self) -> None:
        if self.filepath.exists():
            self._datos = load_db_dat(self.filepath)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: Practica) -> bool:
        self._cargar_datos()

        if entidad.id_pr is None or entidad.id_pr <= 0:
            current_ids = [p.id_pr for p in self._datos]
            entidad.id_pr = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, p in enumerate(self._datos):
                if p.id_pr == entidad.id_pr:
                    self._datos[idx] = entidad
                    break
            else:
                return False

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [p for p in self._datos if p.id_pr != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_pr: int) -> Optional[Practica]:
        self._cargar_datos()
        for p in self._datos:
            if p.id_pr == id_pr:
                return p
        return None

    def buscar_practica_activa_estudiante(self, id_p_estudiante: int) -> Optional[Practica]:
        self._cargar_datos()
        postulaciones_path = Path("storage/db/postulaciones.dat")
        if not postulaciones_path.exists():
            return None
        postulaciones = load_db_dat(postulaciones_path)

        student_pos_ids = {p.id_pos for p in postulaciones if p.id_p_estudiante == id_p_estudiante}
        for pr in self._datos:
            if pr.id_pos in student_pos_ids and pr.estado_de_practica in (
                "Iniciada",
                "En Evaluacion",
            ):
                return pr
        return None

    def buscar_por_estudiante(self, id_p_estudiante: int) -> Optional[Practica]:
        return self.buscar_practica_activa_estudiante(id_p_estudiante)
