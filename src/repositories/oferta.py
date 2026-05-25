import pickle
from pathlib import Path
from typing import Any, Optional

from src.models import Oferta
from src.repositories.interfaces.oferta import OfertaRepositoryABC


class OfertaRepository(OfertaRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/ofertas.dat")
        self._datos: list[Oferta] = []

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

    def guardar(self, entidad: Oferta) -> bool:
        self._cargar_datos()

        if not entidad.id_o:
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

        for idx, o in enumerate(self._datos):
            if o.id_o == entidad.id_o and o.id_e == entidad.id_e:
                self._datos[idx] = entidad
                break
        else:
            self._datos.append(entidad)

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

    def listar_ofertas_disponibles(self) -> list[Oferta]:
        self._cargar_datos()
        return list(self._datos)
