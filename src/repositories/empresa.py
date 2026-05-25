import json
import pickle
from pathlib import Path
from typing import Optional

from src.models import Empresa
from src.repositories.interfaces.base import RepositoryABC


class EmpresaRepository(RepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/empresas.dat")
        self._datos: list[Empresa] = []

    def _cargar_datos(self) -> None:
        json_path = Path("storage/db/empresas.json")

        if not self.filepath.exists() and json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            self._datos = []
            for item in raw_data:
                emp = Empresa(
                    id_e=item["id_e"],
                    nombre_empresa=item["nombre_empresa"],
                    estado_de_convenio_emp=item["estado_de_convenio_emp"],
                )
                if "numeros_contacto" in item:
                    emp.numeros_contacto = item["numeros_contacto"]
                if "correos_contacto" in item:
                    emp.correos_contacto = item["correos_contacto"]
                if "direcciones" in item:
                    emp.direcciones = item["direcciones"]
                self._datos.append(emp)

            self._guardar_datos()
        elif self.filepath.exists():
            with open(self.filepath, "rb") as f:
                self._datos = pickle.load(f)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "wb") as f:
            pickle.dump(self._datos, f)

    def guardar(self, entidad: Empresa) -> bool:
        self._cargar_datos()

        if entidad.id_e is None or entidad.id_e <= 0:
            current_ids = [e.id_e for e in self._datos]
            entidad.id_e = max(current_ids) + 1 if current_ids else 1

        for idx, e in enumerate(self._datos):
            if e.id_e == entidad.id_e:
                self._datos[idx] = entidad
                break
        else:
            self._datos.append(entidad)

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [e for e in self._datos if e.id_e != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_e: int) -> Optional[Empresa]:
        self._cargar_datos()
        for e in self._datos:
            if e.id_e == id_e:
                return e
        return None
