from pathlib import Path
from typing import Optional

from src.models import CartaCompromiso
from src.repositories.interfaces.carta_compromiso_repository_abc import CartaCompromisoRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class CartaCompromisoRepository(CartaCompromisoRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/cartas_compromiso.dat")
        self._datos: list[CartaCompromiso] = []

    def _cargar_datos(self) -> None:
        if self.filepath.exists():
            self._datos = load_db_dat(self.filepath)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: CartaCompromiso) -> bool:
        self._cargar_datos()

        if entidad.id_carta is None or entidad.id_carta <= 0:
            current_ids = [c.id_carta for c in self._datos]
            entidad.id_carta = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, c in enumerate(self._datos):
                if c.id_carta == entidad.id_carta:
                    self._datos[idx] = entidad
                    break
            else:
                self._datos.append(entidad)

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [c for c in self._datos if c.id_carta != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_carta: int) -> Optional[CartaCompromiso]:
        self._cargar_datos()
        for c in self._datos:
            if c.id_carta == id_carta:
                return c
        return None

    def buscar_por_practica(self, id_pr: int) -> Optional[CartaCompromiso]:
        self._cargar_datos()
        for c in self._datos:
            if c.id_pr == id_pr:
                return c
        return None
