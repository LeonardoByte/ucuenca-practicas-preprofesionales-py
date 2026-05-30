from typing import Any, Optional

from src.models import (
    Administrador,
    CoordinadorDePracticas,
    Empresa,
    EstadoConvenio,
    EstadoMatricula,
    EstadoPracticaEstudiante,
    Estudiante,
    RolUsuario,
    TutorAcademico,
    TutorEmpresarial,
    Usuario,
)
from src.repositories import (
    AdministradorRepository,
    CoordinadorRepository,
    EmpresaRepository,
    EstudianteRepository,
    TutorAcademicoRepository,
    TutorEmpresarialRepository,
    UsuarioRepository,
)
from src.services.exceptions import (
    CorreoDuplicadoError,
    CredencialesInvalidasError,
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

    def verificar_credenciales(
        self, correo_electronico: str, contrasena: str
    ) -> Optional[Any]:
        user = self.usuario_repo.buscar_por_username(correo_electronico)
        if not user or user.contrasena != contrasena:
            raise CredencialesInvalidasError(
                "El usuario no existe o la contraseña ingresada es incorrecta."
            )

        match user.rol:
            case RolUsuario.ESTUDIANTE:
                return self.estudiante_repo.buscar_por_id(user.id_p)
            case RolUsuario.COORDINADOR:
                return self.coordinador_repo.buscar_por_id(user.id_p)
            case RolUsuario.TUTOR_ACADEMICO:
                return self.tutor_acad_repo.buscar_por_id(user.id_p)
            case RolUsuario.TUTOR_EMPRESARIAL:
                return self.tutor_emp_repo.buscar_por_id(user.id_p)
            case RolUsuario.EMPRESARIO:
                return self.empresa_repo.buscar_por_id(user.id_p)
            case RolUsuario.ADMINISTRADOR:
                return self.administrador_repo.buscar_por_id(user.id_p)
            case _:
                raise CredencialesInvalidasError(
                    "El usuario no existe o la contraseña ingresada es incorrecta."
                )

    def registrar_nuevo_perfil_sistema(
        self,
        username_correo: str,
        contrasena: str,
        rol: RolUsuario,
        datos_perfil: dict
    ) -> Optional[Any]:
        existing_user = self.usuario_repo.buscar_por_username(username_correo)
        if existing_user:
            raise CorreoDuplicadoError(
                "El correo electrónico ya se encuentra registrado en el sistema."
            )

        profile_entity = None
        profile_id = 0

        match rol:
            case RolUsuario.ESTUDIANTE:
                profile_entity = Estudiante(
                    id_p=0,
                    nombre_y_apellido=datos_perfil.get("nombre_y_apellido", ""),
                    cedula_dni=datos_perfil.get("cedula_dni", ""),
                    correo_electronico=username_correo,
                    direccion=datos_perfil.get("direccion", ""),
                    ciclo_actual=datos_perfil.get("ciclo_actual", 6),
                    estado_de_matricula=datos_perfil.get(
                        "estado_de_matricula", EstadoMatricula.MATRICULADO
                    ),
                    malla_academica=datos_perfil.get("malla_academica", ""),
                    curriculum_vitae=datos_perfil.get("curriculum_vitae", ""),
                    historial_practicas=datos_perfil.get("historial_practicas", ""),
                    estado_practica=datos_perfil.get(
                        "estado_practica", EstadoPracticaEstudiante.SIN_PRACTICAS
                    ),
                )
                if not self.estudiante_repo.guardar(profile_entity):
                    return None
                profile_id = profile_entity.id_p

            case RolUsuario.COORDINADOR:
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

            case RolUsuario.TUTOR_ACADEMICO:
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

            case RolUsuario.TUTOR_EMPRESARIAL:
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

            case RolUsuario.ADMINISTRADOR:
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

            case RolUsuario.EMPRESARIO:
                profile_entity = Empresa(
                    id_e=0,
                    nombre_empresa=datos_perfil.get("nombre_empresa", ""),
                    estado_de_convenio_emp=datos_perfil.get(
                        "estado_de_convenio_emp", EstadoConvenio.VIGENTE
                    ),
                    correo_electronico=username_correo,
                )
                if not self.empresa_repo.guardar(profile_entity):
                    return None
                profile_id = profile_entity.id_e

            case _:
                return None

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
            case RolUsuario.ESTUDIANTE:
                eliminado_perfil = self.estudiante_repo.eliminar(user.id_p)
            case RolUsuario.COORDINADOR:
                eliminado_perfil = self.coordinador_repo.eliminar(user.id_p)
            case RolUsuario.TUTOR_ACADEMICO:
                eliminado_perfil = self.tutor_acad_repo.eliminar(user.id_p)
            case RolUsuario.TUTOR_EMPRESARIAL:
                eliminado_perfil = self.tutor_emp_repo.eliminar(user.id_p)
            case RolUsuario.ADMINISTRADOR:
                eliminado_perfil = self.administrador_repo.eliminar(user.id_p)
            case RolUsuario.EMPRESARIO:
                eliminado_perfil = self.empresa_repo.eliminar(user.id_p)
            case _:
                return False

        if not eliminado_perfil:
            return False

        return self.usuario_repo.eliminar(user.id_u)
