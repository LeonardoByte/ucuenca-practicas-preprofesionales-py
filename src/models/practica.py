from typing import Optional


class Postulacion:
    def __init__(
        self,
        id_pos: int,
        id_p_estudiante: int,
        id_o: str,
        id_e: int,
        id_p_coordinador: int,
        fecha_postulacion: str,
        estado_de_postulacion: str,
    ):
        self.id_pos = id_pos
        self.id_p_estudiante = id_p_estudiante
        self.id_o = id_o  # FK compuesta hacia Oferta
        self.id_e = id_e  # FK compuesta hacia Oferta
        self.id_p_coordinador = id_p_coordinador
        self.fecha_postulacion = fecha_postulacion
        self.estado_de_postulacion = (
            estado_de_postulacion  # "Pendiente", "Validada", "Aceptada", "Rechazada"
        )
        self.id_terna: Optional[int] = None  # Resuelve el agrupamiento lógico de ternas


class Practica:
    def __init__(
        self,
        id_pr: int,
        id_pos: int,
        id_p_tutor_acad: int,
        id_p_tutor_emp: int,
        fecha_inicio: str,
        fecha_fin: str,
        estado_de_practica: str,
    ):
        self.id_pr = id_pr
        self.id_pos = id_pos  # Relación 1 a 1 hacia Postulacion
        self.id_p_tutor_acad = id_p_tutor_acad
        self.id_p_tutor_emp = id_p_tutor_emp
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado_de_practica = (
            estado_de_practica  # "Iniciada", "En Evaluacion", "Finalizada", "Aprobada"
        )


class Actividad:
    def __init__(
        self,
        id_act: int,
        id_pr: int,
        descripcion_de_la_tarea: str,
        estado_de_validacion: str,
    ):
        self.id_act = id_act  # PK compuesta junto con id_pr
        self.id_pr = id_pr
        self.descripcion_de_la_tarea = descripcion_de_la_tarea
        self.estado_de_validacion = (
            estado_de_validacion  # "Propuesta", "Validada", "Rechazada"
        )


class Formulario:
    def __init__(
        self,
        id_doc: int,
        id_pr: int,
        tipo_formulario: str,
        estado_de_firma: str,
        fecha_de_entrega_registro: str,
        numero_formulario: str,
    ):
        self.id_doc = id_doc  # PK compuesta junto con id_pr
        self.id_pr = id_pr
        self.tipo_formulario = (
            tipo_formulario  # "Formulario 1", "Formulario 2", "Formulario 3"
        )
        self.estado_de_firma = (
            estado_de_firma  # "Presentado", "Completado", "Aprobado"
        )
        self.fecha_de_entrega_registro = fecha_de_entrega_registro
        self.numero_formulario = numero_formulario
