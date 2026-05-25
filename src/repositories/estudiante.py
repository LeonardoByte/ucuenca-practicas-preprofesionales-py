import json
import pickle
from pathlib import Path
from typing import Optional

from src.models import (
    CoordinadorDePracticas,
    Estudiante,
    Persona,
    Personal,
    TutorAcademico,
    TutorEmpresarial,
)
from src.repositories.interfaces.estudiante import EstudianteRepositoryABC


class EstudianteRepository(EstudianteRepositoryABC):
    def __init__(self) -> None:
        self.filepath = Path("storage/db/personas.dat")
        self._datos: list[Persona] = []

    def _cargar_datos(self) -> None:
        json_path = Path("storage/db/personas.json")

        if not self.filepath.exists() and json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            self._datos = []
            for item in raw_data:
                rol = item.get("rol")
                if rol == "Estudiante":
                    obj = Estudiante(
                        id_p=item["id_p"],
                        nombre_y_apellido=item["nombre_y_apellido"],
                        cedula_dni=item["cedula_dni"],
                        correo_electronico=item["correo_electronico"],
                        direccion=item["direccion"],
                        ciclo_actual=item["ciclo_actual"],
                        estado_de_matricula=item["estado_de_matricula"],
                        malla_academica=item["malla_academica"],
                        curriculum_vitae=item["curriculum_vitae"],
                        historial_practicas=item["historial_practicas"],
                        estado_practica=item["estado_practica"],
                    )
                elif rol == "Personal":
                    rol_personal = item.get("rol_personal")
                    if rol_personal == "Coordinador":
                        obj = CoordinadorDePracticas(
                            id_p=item["id_p"],
                            nombre_y_apellido=item["nombre_y_apellido"],
                            cedula_dni=item["cedula_dni"],
                            correo_electronico=item["correo_electronico"],
                            direccion=item["direccion"],
                        )
                    elif rol_personal == "Tutor Academico":
                        obj = TutorAcademico(
                            id_p=item["id_p"],
                            nombre_y_apellido=item["nombre_y_apellido"],
                            cedula_dni=item["cedula_dni"],
                            correo_electronico=item["correo_electronico"],
                            direccion=item["direccion"],
                        )
                    elif rol_personal == "Tutor Empresarial":
                        obj = TutorEmpresarial(
                            id_p=item["id_p"],
                            nombre_y_apellido=item["nombre_y_apellido"],
                            cedula_dni=item["cedula_dni"],
                            correo_electronico=item["correo_electronico"],
                            direccion=item["direccion"],
                            id_e=item["id_e"],
                        )
                    else:
                        obj = Personal(
                            id_p=item["id_p"],
                            nombre_y_apellido=item["nombre_y_apellido"],
                            cedula_dni=item["cedula_dni"],
                            correo_electronico=item["correo_electronico"],
                            direccion=item["direccion"],
                            rol_personal=rol_personal,
                        )
                else:
                    obj = Persona(
                        id_p=item["id_p"],
                        nombre_y_apellido=item["nombre_y_apellido"],
                        cedula_dni=item["cedula_dni"],
                        correo_electronico=item["correo_electronico"],
                        direccion=item["direccion"],
                        rol=rol or "Persona",
                    )

                if "telefonos" in item:
                    obj.telefonos = item["telefonos"]
                self._datos.append(obj)

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

    def guardar(self, entidad: Estudiante) -> bool:
        self._cargar_datos()

        if entidad.id_p is None or entidad.id_p <= 0:
            current_ids = [p.id_p for p in self._datos]
            entidad.id_p = max(current_ids) + 1 if current_ids else 1

        for idx, p in enumerate(self._datos):
            if p.id_p == entidad.id_p:
                self._datos[idx] = entidad
                break
        else:
            self._datos.append(entidad)

        self._guardar_datos()
        return True

    def eliminar(self, id_entidad: int) -> bool:
        self._cargar_datos()
        original_len = len(self._datos)
        self._datos = [p for p in self._datos if p.id_p != id_entidad]
        if len(self._datos) < original_len:
            self._guardar_datos()
            return True
        return False

    def buscar_por_id(self, id_p: int) -> Optional[Estudiante]:
        self._cargar_datos()
        for p in self._datos:
            if p.id_p == id_p and isinstance(p, Estudiante):
                return p
        return None

    def buscar_por_cedula(self, cedula: str) -> Optional[Estudiante]:
        self._cargar_datos()
        for p in self._datos:
            if p.cedula_dni == cedula and isinstance(p, Estudiante):
                return p
        return None

    def buscar_persona_por_id(self, id_p: int) -> Optional[Persona]:
        self._cargar_datos()
        for p in self._datos:
            if p.id_p == id_p:
                return p
        return None
