from typing import Optional


class SolicitudAutorizacion:
    def __init__(
        self,
        id_sol_aut: int,
        id_p_estudiante: int,  # (Clave Foránea -> Estudiante)
        nombre_empresa: str,
        detalles_empresa: str,
        fecha_solicitud: str,
        estado_solicitud: str,  # "Pendiente", "Aprobada", "Rechazada"
    ):
        self.id_sol_aut = id_sol_aut
        self.id_p_estudiante = id_p_estudiante
        self.nombre_empresa = nombre_empresa
        self.detalles_empresa = detalles_empresa
        self.fecha_solicitud = fecha_solicitud
        self.estado_solicitud = estado_solicitud
        self.id_p_coordinador: Optional[int] = None


class SolicitudOficio:
    def __init__(
        self,
        id_sol_of: int,
        id_p_estudiante: int,  # (Clave Foránea -> Estudiante)
        nombre_destinatario: str,
        cargo_destinatario: str,
        nombre_empresa: str,
        fecha_solicitud: str,
        estado_solicitud: str,  # "Pendiente", "Emitida", "Rechazada"
    ):
        self.id_sol_of = id_sol_of
        self.id_p_estudiante = id_p_estudiante
        self.nombre_destinatario = nombre_destinatario
        self.cargo_destinatario = cargo_destinatario
        self.nombre_empresa = nombre_empresa
        self.fecha_solicitud = fecha_solicitud
        self.estado_solicitud = estado_solicitud
        self.ruta_oficio_pdf: Optional[str] = None
        self.id_p_coordinador: Optional[int] = None


class CartaCompromiso:
    def __init__(
        self,
        id_carta: int,
        id_pr: int,  # (Clave Foránea -> Practica)
        ruta_pdf: str,
        estado: str,  # "Pendiente", "Entregada", "Firmada"
    ):
        self.id_carta = id_carta
        self.id_pr = id_pr
        self.ruta_pdf = ruta_pdf
        self.estado = estado
