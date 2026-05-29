from pathlib import Path
from typing import Optional

from src.models import SolicitudOficio
from src.repositories.interfaces.solicitud_oficio_repository_abc import SolicitudOficioRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class SolicitudOficioRepository(SolicitudOficioRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/solicitudes_oficio.dat")
        self._datos: list[SolicitudOficio] = []

    def _cargar_datos(self) -> None:
        if self.filepath.exists():
            self._datos = load_db_dat(self.filepath)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: SolicitudOficio) -> bool:
        self._cargar_datos()

        if entidad.id_sol_of is None or entidad.id_sol_of <= 0:
            current_ids = [s.id_sol_of for s in self._datos]
            entidad.id_sol_of = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, s in enumerate(self._datos):
                if s.id_sol_of == entidad.id_sol_of:
                    self._datos[idx] = entidad
                    break
            else:
                self._datos.append(entidad)

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [s for s in self._datos if s.id_sol_of != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_sol_of: int) -> Optional[SolicitudOficio]:
        self._cargar_datos()
        for s in self._datos:
            if s.id_sol_of == id_sol_of:
                return s
        return None

    def listar_por_estudiante(self, id_p_estudiante: int) -> list[SolicitudOficio]:
        self._cargar_datos()
        return [s for s in self._datos if s.id_p_estudiante == id_p_estudiante]

    def obtener_todos(self) -> list[SolicitudOficio]:
        self._cargar_datos()
        return list(self._datos)
