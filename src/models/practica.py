from typing import Optional


class Postulacion:
    def __init__(
        self,
        id_pos: int,
        id_p_estudiante: int,  # (Clave Foránea -> Estudiante)
        id_o: str,  # (Clave Foránea -> Oferta)
        id_e: int,  # (Clave Foránea -> Empresa)
        id_p_coordinador: int,  # (Clave Foránea -> Coordinador)
        fecha_postulacion: str,
        estado_de_postulacion: str,  # "Pendiente", "Validada", "Aceptada", "Rechazada"
    ):
        self.id_pos = id_pos
        self.id_p_estudiante = id_p_estudiante
        self.id_o = id_o
        self.id_e = id_e
        self.id_p_coordinador = id_p_coordinador
        self.fecha_postulacion = fecha_postulacion
        self.estado_de_postulacion = estado_de_postulacion
        self.id_terna: Optional[int] = None  # Resuelve el agrupamiento lógico de ternas


class Practica:
    def __init__(
        self,
        id_pr: int,
        id_pos: int,  # Relación 1 a 1 hacia Postulacion
        id_p_tutor_acad: int,  # (Clave Foránea -> Profesor)
        id_p_tutor_emp: int,  # (Clave Foránea -> Profesor)
        fecha_inicio: str,
        fecha_fin: str,
        estado_de_practica: str,  # "Iniciada", "En Evaluacion", "Finalizada", "Aprobada"
    ):
        self.id_pr = id_pr
        self.id_pos = id_pos
        self.id_p_tutor_acad = id_p_tutor_acad
        self.id_p_tutor_emp = id_p_tutor_emp
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado_de_practica = estado_de_practica


class Actividad:
    def __init__(
        self,
        id_act: int,
        id_pr: int,  # (Clave Foránea -> Practica)
        descripcion_de_la_tarea: str,
        estado_de_validacion: str,  # "Propuesta", "Validada", "Rechazada"
    ):
        self.id_act = id_act
        self.id_pr = id_pr
        self.descripcion_de_la_tarea = descripcion_de_la_tarea
        self.estado_de_validacion = estado_de_validacion


class Formulario:
    def __init__(
        self,
        id_doc: int,
        id_pr: int,  # (Clave Foránea -> Practica)
        tipo_formulario: str,  # "Formulario 1", "Formulario 2", "Formulario 3"
        estado_de_firma: str,  # "Presentado", "Completado", "Aprobado"
        fecha_de_entrega_registro: str,
        numero_formulario: str,
    ):
        self.id_doc = id_doc
        self.id_pr = id_pr
        self.tipo_formulario = tipo_formulario
        self.estado_de_firma = estado_de_firma
        self.fecha_de_entrega_registro = fecha_de_entrega_registro
        self.numero_formulario = numero_formulario
