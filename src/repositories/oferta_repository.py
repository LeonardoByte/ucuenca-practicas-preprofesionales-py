from pathlib import Path
from typing import Any, Optional

from src.models import Oferta
from src.repositories.interfaces.oferta_repository_abc import OfertaRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class OfertaRepository(OfertaRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/ofertas.dat")
        self._datos: list[Oferta] = []

    def _cargar_datos(self) -> None:
        if self.filepath.exists():
            self._datos = load_db_dat(self.filepath)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: Oferta) -> bool:
        self._cargar_datos()

        if entidad.id_o is None or entidad.id_o <= 0:
            current_ids = [o.id_o for o in self._datos if isinstance(o.id_o, int)]
            entidad.id_o = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, o in enumerate(self._datos):
                if o.id_o == entidad.id_o:
                    self._datos[idx] = entidad
                    break
            else:
                self._datos.append(entidad)

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: Any) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        if isinstance(id_entidad, tuple) and len(id_entidad) == 2:
            id_o, id_e = id_entidad
            self._datos = [o for o in self._datos if not (o.id_o == id_o and o.id_e == id_e)]
        else:
            self._datos = [o for o in self._datos if o.id_o != id_entidad]

        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_clave_compuesta(self, id_o: int, id_e: int) -> Optional[Oferta]:
        self._cargar_datos()
        for o in self._datos:
            if o.id_o == id_o and o.id_e == id_e:
                return o
        return None

    def buscar_por_id(self, id_o: int) -> Optional[Oferta]:
        self._cargar_datos()
        for o in self._datos:
            if o.id_o == id_o:
                return o
        return None

    def listar_todas(self) -> list[Oferta]:
        self._cargar_datos()
        return list(self._datos)

    def listar_por_empresa(self, id_e: int) -> list[Oferta]:
        self._cargar_datos()
        return [o for o in self._datos if o.id_e == id_e]

    def listar_ofertas_disponibles(self) -> list[Oferta]:
        self._cargar_datos()
        return [
            o for o in self._datos
            if getattr(o, "validada_por_coordinador", False) is True and getattr(o, "activo", True) is True
        ]

    def obtener_todos(self) -> list[Oferta]:
        self._cargar_datos()
        return list(self._datos)
