from .estados import EstadoMatricula, EstadoPracticaEstudiante, RolPersona, RolPersonal


class Persona:
    def __init__(
        self,
        id_p: int,
        nombre_y_apellido: str,
        cedula_dni: str,
        correo_electronico: str,
        direccion: str,
        rol: RolPersona,
    ):
        self.id_p = id_p
        self.nombre_y_apellido = nombre_y_apellido
        self.cedula_dni = cedula_dni
        self.correo_electronico = correo_electronico
        self.direccion = direccion
        self.rol = rol
        self.telefonos: list[str] = []  # Resuelve la tabla Persona_Telefono (1 a N)


class Estudiante(Persona):
    def __init__(
        self,
        id_p: int,
        nombre_y_apellido: str,
        cedula_dni: str,
        correo_electronico: str,
        direccion: str,
        ciclo_actual: int,
        estado_de_matricula: EstadoMatricula,
        malla_academica: str,  # Ruta local del archivo PDF
        curriculum_vitae: str,  # Ruta local del archivo PDF
        historial_practicas: str,
        estado_practica: EstadoPracticaEstudiante,
    ):
        super().__init__(
            id_p,
            nombre_y_apellido,
            cedula_dni,
            correo_electronico,
            direccion,
            rol=RolPersona.ESTUDIANTE,
        )
        self.ciclo_actual = ciclo_actual
        self.estado_de_matricula = estado_de_matricula
        self.malla_academica = malla_academica
        self.curriculum_vitae = curriculum_vitae
        self.historial_practicas = historial_practicas
        self.estado_practica = estado_practica


class Personal(Persona):
    def __init__(
        self,
        id_p: int,
        nombre_y_apellido: str,
        cedula_dni: str,
        correo_electronico: str,
        direccion: str,
        rol_personal: RolPersonal,
    ):
        super().__init__(
            id_p,
            nombre_y_apellido,
            cedula_dni,
            correo_electronico,
            direccion,
            rol=RolPersona.PERSONAL,
        )
        self.rol_personal = rol_personal


class CoordinadorDePracticas(Personal):
    def __init__(
        self,
        id_p: int,
        nombre_y_apellido: str,
        cedula_dni: str,
        correo_electronico: str,
        direccion: str,
    ):
        super().__init__(
            id_p,
            nombre_y_apellido,
            cedula_dni,
            correo_electronico,
            direccion,
            rol_personal=RolPersonal.COORDINADOR,
        )


class TutorAcademico(Personal):
    def __init__(
        self,
        id_p: int,
        nombre_y_apellido: str,
        cedula_dni: str,
        correo_electronico: str,
        direccion: str,
    ):
        super().__init__(
            id_p,
            nombre_y_apellido,
            cedula_dni,
            correo_electronico,
            direccion,
            rol_personal=RolPersonal.TUTOR_ACADEMICO,
        )


class TutorEmpresarial(Personal):
    def __init__(
        self,
        id_p: int,
        nombre_y_apellido: str,
        cedula_dni: str,
        correo_electronico: str,
        direccion: str,
        id_e: int,  # (Clave Foránea -> Empresa)
    ):
        super().__init__(
            id_p,
            nombre_y_apellido,
            cedula_dni,
            correo_electronico,
            direccion,
            rol_personal=RolPersonal.TUTOR_EMPRESARIAL,
        )
        self.id_e = id_e


class Administrador(Personal):
    def __init__(
        self,
        id_p: int,
        nombre_y_apellido: str,
        cedula_dni: str,
        correo_electronico: str,
        direccion: str,
    ):
        super().__init__(
            id_p,
            nombre_y_apellido,
            cedula_dni,
            correo_electronico,
            direccion,
            rol_personal=RolPersonal.ADMINISTRADOR,
        )
