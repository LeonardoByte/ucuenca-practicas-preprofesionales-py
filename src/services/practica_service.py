from typing import Optional

from src.models import (
    Actividad,
    CartaCompromiso,
    EstadoCartaCompromiso,
    EstadoFirmaFormulario,
    EstadoPractica,
    EstadoValidacionActividad,
    Formulario,
    Practica,
    TipoFormulario,
)
from src.repositories import (
    ActividadRepository,
    CartaCompromisoRepository,
    EstudianteRepository,
    FormularioRepository,
    PostulacionRepository,
    PracticaRepository,
)
from src.services.exceptions import EstudianteConPracticaActivaError
from src.services.interfaces.practica_service_abc import PracticaServiceABC


class PracticaService(PracticaServiceABC):
    def __init__(
        self,
        practica_repo: Optional[PracticaRepository] = None,
        postulacion_repo: Optional[PostulacionRepository] = None,
        estudiante_repo: Optional[EstudianteRepository] = None,
        actividad_repo: Optional[ActividadRepository] = None,
        formulario_repo: Optional[FormularioRepository] = None,
        carta_repo: Optional[CartaCompromisoRepository] = None,
    ) -> None:
        self.practica_repo = practica_repo or PracticaRepository()
        self.postulacion_repo = postulacion_repo or PostulacionRepository()
        self.estudiante_repo = estudiante_repo or EstudianteRepository()
        self.actividad_repo = actividad_repo or ActividadRepository()
        self.formulario_repo = formulario_repo or FormularioRepository()
        self.carta_repo = carta_repo or CartaCompromisoRepository()

    def formalizar_practica(
        self, id_pos_aceptada: int, id_p_tutor_emp: int, fecha_inicio: str, fecha_fin: str
    ) -> Optional[Practica]:
        post = self.postulacion_repo.buscar_por_id(id_pos_aceptada)
        if not post:
            return None

        estudiante = self.estudiante_repo.buscar_por_id(post.id_p_estudiante)
        if not estudiante:
            return None

        # Verificar concurrencia
        est_practica_str = (
            estudiante.estado_practica.value
            if hasattr(estudiante.estado_practica, "value")
            else estudiante.estado_practica
        )
        if str(est_practica_str).upper() == "ACTIVA":
            raise EstudianteConPracticaActivaError(
                f"El estudiante {estudiante.nombre_y_apellido} ya posee una práctica activa."
            )

        # Aceptar la postulación
        post.estado_de_postulacion = "Aceptada"
        self.postulacion_repo.guardar(post)

        # Rechazar las demás postulaciones de la misma oferta
        self.postulacion_repo._cargar_datos()
        for p in self.postulacion_repo._datos:
            if p.id_o == post.id_o and p.id_pos != post.id_pos:
                p.estado_de_postulacion = "Rechazada"
                self.postulacion_repo.guardar(p)

        # Cambiar el estado del estudiante a activo
        estudiante.estado_practica = "Activa"
        self.estudiante_repo.guardar(estudiante)

        # Crear y guardar la práctica
        practica = Practica(
            id_pr=0,
            id_pos=id_pos_aceptada,
            id_p_tutor_acad=0,
            id_p_tutor_emp=id_p_tutor_emp,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado_de_practica=EstadoPractica.INICIADA
        )
        if self.practica_repo.guardar(practica):
            return practica
        return None

    def asignar_tutor_academico(self, id_pr: int, id_p_tutor_acad: int) -> bool:
        practica = self.practica_repo.buscar_por_id(id_pr)
        if not practica:
            return False
        practica.id_p_tutor_acad = id_p_tutor_acad
        return self.practica_repo.guardar(practica)

    def registrar_actividad(self, id_pr: int, descripcion: str) -> Optional[Actividad]:
        act = Actividad(
            id_act=0,
            id_pr=id_pr,
            descripcion_de_la_tarea=descripcion,
            estado_de_validacion=EstadoValidacionActividad.PROPUESTA
        )
        if self.actividad_repo.guardar(act):
            return act
        return None

    def evaluar_actividad(self, id_act: int, id_pr: int, estado: EstadoValidacionActividad) -> bool:
        act = self.actividad_repo.buscar_por_id(id_act)
        if not act or act.id_pr != id_pr:
            return False
        act.estado_de_validacion = estado
        return self.actividad_repo.guardar(act)

    def actualizar_formulario(
        self,
        id_pr: int,
        tipo_formulario: TipoFormulario,
        estado_firma: EstadoFirmaFormulario,
        fecha_entrega: str,
        numero_formulario: str,
    ) -> Optional[Formulario]:
        formularios = self.formulario_repo.listar_formularios_por_practica(id_pr)
        target_form = None

        tipo_form_str = (
            tipo_formulario.value
            if hasattr(tipo_formulario, "value")
            else tipo_formulario
        )

        for f in formularios:
            f_tipo_str = (
                f.tipo_formulario.value
                if hasattr(f.tipo_formulario, "value")
                else f.tipo_formulario
            )
            if str(f_tipo_str) == str(tipo_form_str):
                target_form = f
                break

        if target_form:
            target_form.estado_de_firma = estado_firma
            target_form.fecha_de_entrega_registro = fecha_entrega
            target_form.numero_formulario = numero_formulario
        else:
            target_form = Formulario(
                id_doc=0,
                id_pr=id_pr,
                tipo_formulario=tipo_formulario,
                estado_de_firma=estado_firma,
                fecha_de_entrega_registro=fecha_entrega,
                numero_formulario=numero_formulario
            )

        if self.formulario_repo.guardar(target_form):
            return target_form
        return None

    def registrar_entrega_carta_compromiso(
        self, id_pr: int, ruta_pdf: str, nuevo_estado: EstadoCartaCompromiso
    ) -> bool:
        carta = self.carta_repo.buscar_por_practica(id_pr)
        if carta:
            carta.ruta_pdf = ruta_pdf
            carta.estado = nuevo_estado
        else:
            carta = CartaCompromiso(
                id_carta=0,
                id_pr=id_pr,
                ruta_pdf=ruta_pdf,
                estado=nuevo_estado
            )
        return self.carta_repo.guardar(carta)
