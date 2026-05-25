import pickle
from pathlib import Path
from typing import Optional

from src.models import SolicitudAutorizacion
from src.repositories.interfaces.solicitud_autorizacion import (
    SolicitudAutorizacionRepositoryABC,
)


class SolicitudAutorizacionRepository(SolicitudAutorizacionRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/solicitudes_autorizacion.dat")
        self._datos: list[SolicitudAutorizacion] = []

    def _cargar_datos(self) -> None:
        if self.filepath.exists():
            with open(self.filepath, "rb") as f:
                self._datos = pickle.load(f)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "wb") as f:
            pickle.dump(self._datos, f)

    def guardar(self, entidad: SolicitudAutorizacion) -> bool:
        self._cargar_datos()

        if entidad.id_sol_aut is None or entidad.id_sol_aut <= 0:
            current_ids = [s.id_sol_aut for s in self._datos]
            entidad.id_sol_aut = max(current_ids) + 1 if current_ids else 1

        for idx, s in enumerate(self._datos):
            if s.id_sol_aut == entidad.id_sol_aut:
                self._datos[idx] = entidad
                break
        else:
            self._datos.append(entidad)

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [s for s in self._datos if s.id_sol_aut != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_sol_aut: int) -> Optional[SolicitudAutorizacion]:
        self._cargar_datos()
        for s in self._datos:
            if s.id_sol_aut == id_sol_aut:
                return s
        return None

    def listar_por_estudiante(self, id_p_estudiante: int) -> list[SolicitudAutorizacion]:
        self._cargar_datos()
        return [s for s in self._datos if s.id_p_estudiante == id_p_estudiante]
