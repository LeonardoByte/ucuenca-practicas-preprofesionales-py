class Usuario:
    def __init__(self,
        id_u: int,
        username_correo: str,
        contrasena: str,
        rol: str,
        id_p: int
    ):
        self.id_u = id_u                    # PK Simple Auto-incremental
        self.username_correo = username_correo  # El usuario para loguear (correo electrónico)
        self.contrasena = contrasena        # Contraseña (en texto plano para el proyecto o hash)
        self.rol = rol                      # "Estudiante", "Coordinador", "Tutor Academico", "Tutor Empresarial", "Empresa"
        self.id_p = id_p                    # FK -> Apunta al ID de la persona en su respectivo .dat