import json
import pickle
from pathlib import Path
from typing import Optional


class LoginController:
    def validar_credenciales(
        self, usuario: str, contrasena: str
    ) -> tuple[Optional[str], Optional[int]]:
        dat_path = Path("storage/db/usuarios.dat")
        json_path = Path("storage/db/usuarios.json")

        if not dat_path.exists() and json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            dat_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dat_path, "wb") as f:
                pickle.dump(data, f)

        if dat_path.exists():
            with open(dat_path, "rb") as f:
                usuarios = pickle.load(f)
        else:
            usuarios = []

        for u in usuarios:
            if isinstance(u, dict):
                u_user = u.get("usuario")
                u_pass = u.get("contrasena")
                u_rol = u.get("rol")
                u_id = u.get("id_p") if u.get("id_p") is not None else u.get("id_e")
            else:
                u_user = getattr(u, "usuario", None)
                u_pass = getattr(u, "contrasena", None)
                u_rol = getattr(u, "rol", None)
                u_id = (
                    getattr(u, "id_p", None)
                    if getattr(u, "id_p", None) is not None
                    else getattr(u, "id_e", None)
                )

            if u_user == usuario and u_pass == contrasena:
                return u_rol, u_id

        return None, None
