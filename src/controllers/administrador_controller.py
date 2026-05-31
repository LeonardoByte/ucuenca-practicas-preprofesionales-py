from PyQt6.QtCore import QObject, pyqtSignal

from src.models.estados import RolUsuario
from src.services.interfaces.administrador_main_service_abc import AdministradorMainServiceABC


class AdministradorController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: AdministradorMainServiceABC) -> None:
        super().__init__()
        self.view = view
        self.service = service

        # Navigation connections
        if hasattr(self.view, "btn_nav_ver_usuarios") and self.view.btn_nav_ver_usuarios:
            self.view.btn_nav_ver_usuarios.clicked.connect(self.ir_a_ver_usuarios)
        if hasattr(self.view, "btn_nav_crear_usuario") and self.view.btn_nav_crear_usuario:
            self.view.btn_nav_crear_usuario.clicked.connect(self.ir_a_crear_usuario)
        if hasattr(self.view, "btn_cerrar_sesion") and self.view.btn_cerrar_sesion:
            self.view.btn_cerrar_sesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Action connections
        if hasattr(self.view, "btn_crear_usuario") and self.view.btn_crear_usuario:
            self.view.btn_crear_usuario.clicked.connect(self.crear_usuario)
        if hasattr(self.view, "btn_eliminar_usuario") and self.view.btn_eliminar_usuario:
            self.view.btn_eliminar_usuario.clicked.connect(self.eliminar_usuario)

        # Initial load
        self.cargar_usuarios()

    def ir_a_ver_usuarios(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("ver_usuarios")
        self.cargar_usuarios()

    def ir_a_crear_usuario(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("crear_usuario")

    def solicitar_cerrar_sesion(self) -> None:
        if hasattr(self.view, "confirmar_accion"):
            if not self.view.confirmar_accion("¿Está seguro de cerrar sesión?"):
                return
        self.cerrar_sesion.emit()

    def cargar_usuarios(self) -> None:
        try:
            usuarios = self.service.obtener_todos_los_usuarios_sistema()
            if hasattr(self.view, "mostrar_usuarios"):
                self.view.mostrar_usuarios(usuarios)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar usuarios: {str(e)}")

    def crear_usuario(self) -> None:
        try:
            # Gather text fields
            correo = self.view.txt_crear_correo.text().strip()
            contrasena = self.view.txt_crear_contrasena.text().strip()
            nombre = self.view.txt_crear_nombre.text().strip()
            cedula = self.view.txt_crear_cedula.text().strip()
            direccion = self.view.txt_crear_direccion.text().strip()
            rol = self.view.cmb_crear_rol.currentData()

            if not correo or not contrasena or not nombre or not rol:
                self.view.mostrar_error(
                    "Por favor complete los campos obligatorios: Correo, Contraseña, Nombre y Rol."
                )
                return

            datos_perfil = {
                "nombre_y_apellido": nombre,
                "cedula_dni": cedula,
                "direccion": direccion,
                "nombre_empresa": nombre,
            }

            if rol == RolUsuario.TUTOR_EMPRESARIAL:
                try:
                    datos_perfil["id_e"] = int(self.view.txt_crear_id_e.text().strip() or 0)
                except ValueError:
                    self.view.mostrar_error("El ID de la empresa debe ser un número entero.")
                    return

            profile = self.service.crear_cuenta_usuario_sistema(
                correo, contrasena, rol, datos_perfil
            )
            if profile is not None:
                self.view.mostrar_exito("Usuario registrado exitosamente.")
                if hasattr(self.view, "limpiar_formulario_creacion"):
                    self.view.limpiar_formulario_creacion()
                self.ir_a_ver_usuarios()
            else:
                self.view.mostrar_error("No se pudo registrar el usuario.")
        except Exception as e:
            self.view.mostrar_error(f"Error al crear usuario: {str(e)}")

    def eliminar_usuario(self) -> None:
        try:
            correo = None
            if hasattr(self.view, "obtener_usuario_seleccionado"):
                correo = self.view.obtener_usuario_seleccionado()

            if not correo and hasattr(self.view, "txt_eliminar_correo"):
                correo = self.view.txt_eliminar_correo.text().strip()

            if not correo:
                self.view.mostrar_error(
                    "Por favor, seleccione un usuario de la tabla o ingrese el correo."
                )
                return

            if hasattr(self.view, "confirmar_accion"):
                confirm = self.view.confirmar_accion(
                    f"¿Está seguro de que desea eliminar permanentemente al usuario: {correo}?"
                )

            if confirm:
                success = self.service.eliminar_usuario_sistema(correo)
                if success:
                    self.view.mostrar_exito("Usuario eliminado exitosamente.")
                    self.cargar_usuarios()
                else:
                    self.view.mostrar_error(
                        "No se pudo eliminar el usuario (usuario no encontrado o error interno)."
                    )
        except Exception as e:
            self.view.mostrar_error(f"Error al eliminar usuario: {str(e)}")
