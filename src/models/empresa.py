from .estados import EstadoConvenio


class Empresa:
    def __init__(
        self,
        id_e: int,
        nombre_empresa: str,
        estado_de_convenio_emp: EstadoConvenio,
        correo_electronico: str,
    ):
        self.id_e = id_e
        self.nombre_empresa = nombre_empresa
        self.estado_de_convenio_emp = estado_de_convenio_emp
        self.correo_electronico = correo_electronico
        self.numeros_contacto: list[str] = []  # Resuelve tabla Empresa_Numero_Contacto
        self.direcciones: list[str] = []  # Resuelve tabla Empresa_Direccion


class Convenio:
    def __init__(
        self,
        id_con: int,
        id_e: int,  # (Clave Foránea -> Empresa)
        fecha_firma: str,
        fecha_vencimiento: str,
        estado_del_convenio: EstadoConvenio,
    ):
        self.id_con = id_con
        self.id_e = id_e
        self.fecha_firma = fecha_firma
        self.fecha_vencimiento = fecha_vencimiento
        self.estado_del_convenio = estado_del_convenio


class Oferta:
    def __init__(
        self,
        id_o: int,
        id_e: int,  # (Clave Foránea -> Empresa)
        descripcion_oferta: str,
        requisitos: str,
        fecha_de_publicacion: str,
        duracion: str,
        remuneracion: float,
    ):
        self.id_o = id_o
        self.id_e = id_e
        self.descripcion_oferta = descripcion_oferta
        self.requisitos = requisitos
        self.fecha_de_publicacion = fecha_de_publicacion
        self.duracion = duracion
        self.remuneracion = remuneracion
