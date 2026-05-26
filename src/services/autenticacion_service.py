from typing import Optional, Any
from src.models import (
    Usuario,
    Estudiante,
    CoordinadorDePracticas,
    TutorAcademico,
    TutorEmpresarial,
    Administrador,
    Empresa,
)
from src.repositories import (
    UsuarioRepository,
    EstudianteRepository,
    CoordinadorRepository,
    TutorAcademicoRepository,
    TutorEmpresarialRepository,
    AdministradorRepository,
    EmpresaRepository,
)
from src.services.interfaces.autenticacion_service_abc import AutenticacionServiceABC


class AutenticacionService(AutenticacionServiceABC):
    def __init__(
        self,
        usuario_repo: Optional[UsuarioRepository] = None,
        estudiante_repo: Optional[EstudianteRepository] = None,
        coordinador_repo: Optional[CoordinadorRepository] = None,
        tutor_acad_repo: Optional[TutorAcademicoRepository] = None,
        tutor_emp_repo: Optional[TutorEmpresarialRepository] = None,
        empresa_repo: Optional[EmpresaRepository] = None,
        administrador_repo: Optional[AdministradorRepository] = None,
    ) -> None:
        self.usuario_repo = usuario_repo or UsuarioRepository()
        self.estudiante_repo = estudiante_repo or EstudianteRepository()
        self.coordinador_repo = coordinador_repo or CoordinadorRepository()
        self.tutor_acad_repo = tutor_acad_repo or TutorAcademicoRepository()
        self.tutor_emp_repo = tutor_emp_repo or TutorEmpresarialRepository()
        self.empresa_repo = empresa_repo or EmpresaRepository()
        self.administrador_repo = administrador_repo or AdministradorRepository()

    def verificar_credenciales(self, correo_electronico: str, contrasena: str) -> Optional[Any]:
        user = self.usuario_repo.buscar_por_username(correo_electronico)
        if not user or user.contrasena != contrasena:
            return None

        # Dependiendo del rol, buscar y retornar la entidad de perfil completa
        match user.rol:
            case "Estudiante":
                return self.estudiante_repo.buscar_por_id(user.id_p)
            case "Coordinador":
                return self.coordinador_repo.buscar_por_id(user.id_p)
            case "Tutor Academico":
                return self.tutor_acad_repo.buscar_por_id(user.id_p)
            case "Tutor Empresarial":
                return self.tutor_emp_repo.buscar_por_id(user.id_p)
            case "Empresa":
                return self.empresa_repo.buscar_por_id(user.id_p)
            case "Administrador":
                return self.administrador_repo.buscar_por_id(user.id_p)
            case _:
                return None

    def registrar_nuevo_perfil_sistema(
        self,
        username_correo: str,
        contrasena: str,
        rol: str,
        datos_perfil: dict
    ) -> Optional[Any]:
        # Validar que el username_correo no exista
        existing_user = self.usuario_repo.buscar_por_username(username_correo)
        if existing_user:
            return None

        profile_entity = None
        profile_id = 0

        # Crear y persistir el perfil en su respectivo repo para obtener el ID auto-generado
        match rol:
            case "Estudiante":
                profile_entity = Estudiante(
                    id_p=0,
                    nombre_y_apellido=datos_perfil.get("nombre_y_apellido", ""),
                    cedula_dni=datos_perfil.get("cedula_dni", ""),
                    correo_electronico=username_correo,
                    direccion=datos_perfil.get("direccion", ""),
                    ciclo_actual=datos_perfil.get("ciclo_actual", 6),
                    estado_de_matricula=datos_perfil.get("estado_de_matricula", "Matriculado"),
                    malla_academica=datos_perfil.get("malla_academica", ""),
                    curriculum_vitae=datos_perfil.get("curriculum_vitae", ""),
                    historial_practicas=datos_perfil.get("historial_practicas", "Ninguno"),
                    estado_practica=datos_perfil.get("estado_practica", "Sin Practicas"),
                )
                if not self.estudiante_repo.guardar(profile_entity):
                    return None
                profile_id = profile_entity.id_p

            case "Coordinador":
                profile_entity = CoordinadorDePracticas(
                    id_p=0,
                    nombre_y_apellido=datos_perfil.get("nombre_y_apellido", ""),
                    cedula_dni=datos_perfil.get("cedula_dni", ""),
                    correo_electronico=username_correo,
                    direccion=datos_perfil.get("direccion", ""),
                )
                if not self.coordinador_repo.guardar(profile_entity):
                    return None
                profile_id = profile_entity.id_p

            case "Tutor Academico":
                profile_entity = TutorAcademico(
                    id_p=0,
                    nombre_y_apellido=datos_perfil.get("nombre_y_apellido", ""),
                    cedula_dni=datos_perfil.get("cedula_dni", ""),
                    correo_electronico=username_correo,
                    direccion=datos_perfil.get("direccion", ""),
                )
                if not self.tutor_acad_repo.guardar(profile_entity):
                    return None
                profile_id = profile_entity.id_p

            case "Tutor Empresarial":
                profile_entity = TutorEmpresarial(
                    id_p=0,
                    nombre_y_apellido=datos_perfil.get("nombre_y_apellido", ""),
                    cedula_dni=datos_perfil.get("cedula_dni", ""),
                    correo_electronico=username_correo,
                    direccion=datos_perfil.get("direccion", ""),
                    id_e=datos_perfil.get("id_e", 0),
                )
                if not self.tutor_emp_repo.guardar(profile_entity):
                    return None
                profile_id = profile_entity.id_p

            case "Administrador":
                profile_entity = Administrador(
                    id_p=0,
                    nombre_y_apellido=datos_perfil.get("nombre_y_apellido", ""),
                    cedula_dni=datos_perfil.get("cedula_dni", ""),
                    correo_electronico=username_correo,
                    direccion=datos_perfil.get("direccion", ""),
                )
                if not self.administrador_repo.guardar(profile_entity):
                    return None
                profile_id = profile_entity.id_p

            case "Empresa":
                profile_entity = Empresa(
                    id_e=0,
                    nombre_empresa=datos_perfil.get("nombre_empresa", ""),
                    estado_de_convenio_emp=datos_perfil.get("estado_de_convenio_emp", "Vigente"),
                )
                if not self.empresa_repo.guardar(profile_entity):
                    return None
                profile_id = profile_entity.id_e

            case _:
                return None

        # Guardar la entidad Usuario vinculando el profile_id
        usuario = Usuario(
            id_u=0,
            username_correo=username_correo,
            contrasena=contrasena,
            rol=rol,
            id_p=profile_id,
        )
        if not self.usuario_repo.guardar(usuario):
            return None

        return profile_entity

def eliminar_cuenta_usuario_sistema(self, username_correo: str) -> bool:
        user = self.usuario_repo.buscar_por_username(username_correo)
        if not user:
            return False

        eliminado_perfil = False
        match user.rol:
            case "Estudiante":
                eliminado_perfil = self.estudiante_repo.eliminar(user.id_p)
            case "Coordinador":
                eliminado_perfil = self.coordinador_repo.eliminar(user.id_p)
            case "Tutor Academico":
                eliminado_perfil = self.tutor_acad_repo.eliminar(user.id_p)
            case "Tutor Empresarial":
                eliminado_perfil = self.tutor_emp_repo.eliminar(user.id_p)
            case "Administrador":
                eliminado_perfil = self.administrador_repo.eliminar(user.id_p)
            case "Empresa":
                eliminado_perfil = self.empresa_repo.eliminar(user.id_p)
            case _:
                return False

        if not eliminado_perfil:
            return False

        return self.usuario_repo.eliminar(user.id_u)
