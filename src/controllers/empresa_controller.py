from PyQt6.QtCore import QObject, pyqtSignal

from src.services.interfaces.empresa_main_service_abc import EmpresaMainServiceABC


class EmpresaController(QObject):
    cerrar_sesion = pyqtSignal()

    def __init__(self, view, service: EmpresaMainServiceABC, empresa_perfil) -> None:
        super().__init__()
        self.view = view
        self.service = service
        self.empresa_perfil = empresa_perfil

        # Hook navigation
        if hasattr(self.view, "btn_nav_ofertas") and self.view.btn_nav_ofertas:
            self.view.btn_nav_ofertas.clicked.connect(self.ir_a_ofertas)
        if hasattr(self.view, "btn_nav_practicas") and self.view.btn_nav_practicas:
            self.view.btn_nav_practicas.clicked.connect(self.ir_a_practicas)
        if hasattr(self.view, "btn_nav_convenios") and self.view.btn_nav_convenios:
            self.view.btn_nav_convenios.clicked.connect(self.ir_a_convenios)
        if hasattr(self.view, "btn_nav_tutores") and self.view.btn_nav_tutores:
            self.view.btn_nav_tutores.clicked.connect(self.ir_a_tutores)
        if hasattr(self.view, "btn_cerrar_sesion") and self.view.btn_cerrar_sesion:
            self.view.btn_cerrar_sesion.clicked.connect(self.solicitar_cerrar_sesion)

        # Hook actions
        if hasattr(self.view, "btn_crear_convenio") and self.view.btn_crear_convenio:
            self.view.btn_crear_convenio.clicked.connect(self.crear_convenio)
        if hasattr(self.view, "btn_publicar_oferta") and self.view.btn_publicar_oferta:
            self.view.btn_publicar_oferta.clicked.connect(self.publicar_oferta)
        if hasattr(self.view, "cmb_ofertas_activas") and self.view.cmb_ofertas_activas:
            # When selected offer changes, load candidates
            self.view.cmb_ofertas_activas.currentIndexChanged.connect(self.cargar_terna_candidatos)
        if hasattr(self.view, "btn_contratar_candidato") and self.view.btn_contratar_candidato:
            self.view.btn_contratar_candidato.clicked.connect(self.contratar_candidato)

        # Initial load
        self.cargar_convenios()
        self.cargar_tutores()
        self.cargar_ofertas()
        self.cargar_practicas()

    def ir_a_ofertas(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("ofertas")
        self.cargar_ofertas()

    def ir_a_practicas(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("practicas")
        self.cargar_practicas()

    def ir_a_convenios(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("convenios")
        self.cargar_convenios()

    def ir_a_tutores(self) -> None:
        if hasattr(self.view, "mostrar_seccion"):
            self.view.mostrar_seccion("tutores")
        self.cargar_tutores()

    def solicitar_cerrar_sesion(self) -> None:
        if hasattr(self.view, "confirmar_accion"):
            if not self.view.confirmar_accion("¿Está seguro de cerrar sesión?"):
                return
        self.cerrar_sesion.emit()

    def cargar_convenios(self) -> None:
        try:
            convenios = self.service.obtener_convenios_empresa(self.empresa_perfil.id_e)
            if hasattr(self.view, "mostrar_convenios"):
                self.view.mostrar_convenios(convenios)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar convenios: {str(e)}")

    def cargar_tutores(self) -> None:
        try:
            tutores = self.service.obtener_tutores_de_empresa(self.empresa_perfil.id_e)
            if hasattr(self.view, "mostrar_tutores"):
                self.view.mostrar_tutores(tutores)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar tutores: {str(e)}")

    def cargar_ofertas(self) -> None:
        try:
            activas = self.service.obtener_ofertas_activas_empresa(self.empresa_perfil.id_e)
            historial = self.service.obtener_historial_ofertas_empresa(self.empresa_perfil.id_e)
            if hasattr(self.view, "mostrar_ofertas_activas"):
                self.view.mostrar_ofertas_activas(activas)
            if hasattr(self.view, "mostrar_historial_ofertas"):
                self.view.mostrar_historial_ofertas(historial)
            if hasattr(self.view, "poblar_selector_ofertas"):
                self.view.poblar_selector_ofertas(activas)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar ofertas: {str(e)}")

    def cargar_practicas(self) -> None:
        try:
            activas = self.service.obtener_practicas_activas_empresa(self.empresa_perfil.id_e)
            historial = self.service.obtener_historial_practicas_empresa(self.empresa_perfil.id_e)
            if hasattr(self.view, "mostrar_practicas_activas"):
                self.view.mostrar_practicas_activas(activas)
            if hasattr(self.view, "mostrar_historial_practicas"):
                self.view.mostrar_historial_practicas(historial)
        except Exception as e:
            if hasattr(self.view, "mostrar_error"):
                self.view.mostrar_error(f"Error al cargar prácticas: {str(e)}")

    def crear_convenio(self) -> None:
        try:
            fecha_firma = ""
            if hasattr(self.view, "obtener_fecha_firma"):
                fecha_firma = self.view.obtener_fecha_firma()

            fecha_vence = ""
            if hasattr(self.view, "obtener_fecha_vencimiento"):
                fecha_vence = self.view.obtener_fecha_vencimiento()

            if not fecha_firma or not fecha_vence:
                self.view.mostrar_error("Por favor complete las fechas de firma y vencimiento.")
                return

            convenio = self.service.crear_convenio_empresa(
                self.empresa_perfil.id_e, fecha_firma, fecha_vence
            )
            if convenio is not None:
                self.view.mostrar_exito("Convenio registrado exitosamente.")
                self.cargar_convenios()
            else:
                self.view.mostrar_error("No se pudo registrar el convenio.")
        except Exception as e:
            self.view.mostrar_error(f"Error al crear convenio: {str(e)}")

    def publicar_oferta(self) -> None:
        try:
            descripcion = ""
            if hasattr(self.view, "txt_oferta_descripcion"):
                descripcion = self.view.txt_oferta_descripcion.text().strip()

            requisitos = ""
            if hasattr(self.view, "txt_oferta_requisitos"):
                requisitos = self.view.txt_oferta_requisitos.text().strip()

            fecha_pub = ""
            if hasattr(self.view, "obtener_fecha_publicacion"):
                fecha_pub = self.view.obtener_fecha_publicacion()

            duracion = ""
            if hasattr(self.view, "txt_oferta_duracion"):
                duracion = self.view.txt_oferta_duracion.text().strip()

            remuneracion = 0.0
            if hasattr(self.view, "txt_oferta_remuneracion"):
                try:
                    remuneracion = float(self.view.txt_oferta_remuneracion.text().strip() or 0)
                except ValueError:
                    self.view.mostrar_error("La remuneración debe ser un valor decimal.")
                    return

            if not descripcion or not requisitos or not fecha_pub or not duracion:
                self.view.mostrar_error("Por favor complete todos los datos de la oferta.")
                return

            oferta = self.service.registrar_oferta(
                self.empresa_perfil.id_e, descripcion, requisitos, fecha_pub, duracion, remuneracion
            )
            if oferta is not None:
                self.view.mostrar_exito("Oferta publicada con éxito.")
                if hasattr(self.view, "txt_oferta_descripcion"):
                    self.view.txt_oferta_descripcion.clear()
                if hasattr(self.view, "txt_oferta_requisitos"):
                    self.view.txt_oferta_requisitos.clear()
                if hasattr(self.view, "txt_oferta_duracion"):
                    self.view.txt_oferta_duracion.clear()
                if hasattr(self.view, "txt_oferta_remuneracion"):
                    self.view.txt_oferta_remuneracion.clear()
                self.cargar_ofertas()
            else:
                self.view.mostrar_error("No se pudo publicar la oferta.")
        except Exception as e:
            self.view.mostrar_error(f"Error al publicar oferta: {str(e)}")

    def cargar_terna_candidatos(self) -> None:
        try:
            id_o = None
            if hasattr(self.view, "obtener_oferta_seleccionada"):
                id_o = self.view.obtener_oferta_seleccionada()

            if not id_o:
                if hasattr(self.view, "mostrar_candidatos"):
                    self.view.mostrar_candidatos([])
                return

            # Retrieve candidate postulations corresponding to this offer in a terna
            self.service.postulacion_service.postulacion_repo._cargar_datos()
            id_terna = None
            for p in self.service.postulacion_service.postulacion_repo._datos:
                if p.id_o == id_o and p.id_terna is not None:
                    id_terna = p.id_terna
                    break

            candidatos = []
            if id_terna is not None:
                candidatos = self.service.visualizar_terna_recibida(id_terna)

            if hasattr(self.view, "mostrar_candidatos"):
                self.view.mostrar_candidatos(candidatos)
        except Exception as e:
            self.view.mostrar_error(f"Error al cargar candidatos de la terna: {str(e)}")

    def contratar_candidato(self) -> None:
        try:
            id_pos = None
            if hasattr(self.view, "obtener_postulacion_seleccionada"):
                id_pos = self.view.obtener_postulacion_seleccionada()

            id_tutor_emp = None
            if hasattr(self.view, "obtener_tutor_seleccionado"):
                id_tutor_emp = self.view.obtener_tutor_seleccionado()

            fecha_inicio = ""
            if hasattr(self.view, "obtener_fecha_inicio"):
                fecha_inicio = self.view.obtener_fecha_inicio()

            fecha_fin = ""
            if hasattr(self.view, "obtener_fecha_fin"):
                fecha_fin = self.view.obtener_fecha_fin()

            if not id_pos or not id_tutor_emp or not fecha_inicio or not fecha_fin:
                self.view.mostrar_error("Por favor complete todos los datos de contratación.")
                return

            success = self.service.seleccionar_candidato_ganador(
                id_pos, id_tutor_emp, fecha_inicio, fecha_fin
            )
            if success:
                self.view.mostrar_exito(
                    "Contratación completada y práctica formalizada exitosamente."
                )
                self.cargar_ofertas()
                self.cargar_practicas()
                if hasattr(self.view, "limpiar_formulario_contratacion"):
                    self.view.limpiar_formulario_contratacion()
            else:
                self.view.mostrar_error("No se pudo formalizar la práctica.")
        except Exception as e:
            self.view.mostrar_error(f"Error en la contratación: {str(e)}")
