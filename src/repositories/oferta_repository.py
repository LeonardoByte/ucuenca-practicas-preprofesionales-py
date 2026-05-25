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

        is_empty_or_zero = False
        if not entidad.id_o:
            is_empty_or_zero = True
        else:
            try:
                if int(entidad.id_o) <= 0:
                    is_empty_or_zero = True
            except ValueError:
                pass

        if is_empty_or_zero:
            numeric_ids = []
            for o in self._datos:
                if isinstance(o.id_o, int):
                    numeric_ids.append(o.id_o)
                elif isinstance(o.id_o, str) and o.id_o.startswith("O"):
                    try:
                        numeric_ids.append(int(o.id_o[1:]))
                    except ValueError:
                        pass
            next_num = max(numeric_ids) + 1 if numeric_ids else 1
            entidad.id_o = f"O{next_num}"
            self._datos.append(entidad)
        else:
            for idx, o in enumerate(self._datos):
                if o.id_o == entidad.id_o and o.id_e == entidad.id_e:
                    self._datos[idx] = entidad
                    break
            else:
                return False

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: Any) -> bool:
        self._cargar_datos()
        # id_entidad could be a composite key tuple (id_o, id_e) or just string id_o
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

    def buscar_por_clave_compuesta(self, id_o: str, id_e: int) -> Optional[Oferta]:
        self._cargar_datos()
        for o in self._datos:
            if o.id_o == id_o and o.id_e == id_e:
                return o
        return None

    def buscar_por_id(self, id_o: Any) -> Optional[Oferta]:
        self._cargar_datos()
        target = str(id_o)
        for o in self._datos:
            if str(o.id_o) == target:
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
        return list(self._datos)
