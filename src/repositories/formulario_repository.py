from pathlib import Path
from typing import Any, Optional

from src.models import Formulario
from src.repositories.interfaces.formulario_repository_abc import FormularioRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class FormularioRepository(FormularioRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/formularios.dat")
        self._datos: list[Formulario] = []

    def _cargar_datos(self) -> None:
        if self.filepath.exists():
            self._datos = load_db_dat(self.filepath)
        else:
            self._datos = []

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: Formulario) -> bool:
        self._cargar_datos()

        if entidad.id_doc is None or entidad.id_doc <= 0:
            current_ids = [f.id_doc for f in self._datos]
            entidad.id_doc = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, f in enumerate(self._datos):
                if f.id_doc == entidad.id_doc and f.id_pr == entidad.id_pr:
                    self._datos[idx] = entidad
                    break
            else:
                return False

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: Any) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        if isinstance(id_entidad, tuple) and len(id_entidad) == 2:
            id_doc, id_pr = id_entidad
            self._datos = [f for f in self._datos if not (f.id_doc == id_doc and f.id_pr == id_pr)]
        else:
            self._datos = [f for f in self._datos if f.id_doc != id_entidad]

        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_clave_compuesta(self, id_doc: int, id_pr: int) -> Optional[Formulario]:
        self._cargar_datos()
        for f in self._datos:
            if f.id_doc == id_doc and f.id_pr == id_pr:
                return f
        return None

    def buscar_por_id(self, id_doc: int) -> Optional[Formulario]:
        self._cargar_datos()
        for f in self._datos:
            if f.id_doc == id_doc:
                return f
        return None

    def listar_formularios_por_practica(self, id_pr: int) -> list[Formulario]:
        self._cargar_datos()
        return [f for f in self._datos if f.id_pr == id_pr]
