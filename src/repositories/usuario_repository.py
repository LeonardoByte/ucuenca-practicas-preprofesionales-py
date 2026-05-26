from pathlib import Path
from typing import Optional

from src.models.usuario import Usuario
from src.repositories.interfaces.usuario_repository_abc import UsuarioRepositoryABC
from src.utils.serialization import load_db_dat, save_db_dat


class UsuarioRepository(UsuarioRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/usuarios.dat")
        self._datos: list[Usuario] = []

    def _cargar_datos(self) -> None:
        self._datos = load_db_dat(self.filepath)

    def _guardar_datos(self) -> None:
        save_db_dat(self.filepath, self._datos)

    def guardar(self, entidad: Usuario) -> bool:
        self._cargar_datos()

        if entidad.id_u is None or entidad.id_u <= 0:
            current_ids = [u.id_u for u in self._datos]
            entidad.id_u = max(current_ids) + 1 if current_ids else 1
            self._datos.append(entidad)
        else:
            for idx, u in enumerate(self._datos):
                if u.id_u == entidad.id_u:
                    self._datos[idx] = entidad
                    break
            else:
                self._datos.append(entidad)

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [u for u in self._datos if u.id_u != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_username(self, username_cedula: str) -> Optional[Usuario]:
        self._cargar_datos()
        for u in self._datos:
            if u.username_correo == username_cedula:
                return u
        return None
