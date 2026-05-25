from abc import ABC, abstractmethod

from src.models import Actividad, Formulario, Practica


class PracticaServiceABC(ABC):
    @abstractmethod
    def formalizar_practica_estandar(
        self, id_pos_aceptada: int, id_p_tutor_acad: int, id_p_tutor_emp: int
    ) -> Practica:
        """Acepta la postulación seleccionada por la empresa,
        rechaza el resto y crea el Formulario 1.
        """
        pass

    @abstractmethod
    def formalizar_practica_empresa_propia(
        self,
        id_p_estudiante: int,
        id_e: int,
        id_p_coordinador: int,
        id_p_tutor_acad: int,
        id_p_tutor_emp: int,
    ) -> Practica:
        """Formaliza directamente una práctica tras la aprobación del
        coordinador para una empresa propia.
        """
        pass

    @abstractmethod
    def aprobar_solicitud_autorizacion(
        self, id_sol_aut: int, id_p_coordinador: int, aprobar: bool
    ) -> bool:
        """Coordinador aprueba o rechaza la solicitud de empresa propia."""
        pass

    @abstractmethod
    def emitir_oficio(
        self, id_sol_of: int, id_p_coordinador: int, ruta_pdf: str
    ) -> bool:
        """Coordinador emite formalmente el oficio a la empresa."""
        pass

    @abstractmethod
    def registrar_entrega_carta_compromiso(
        self, id_pr: int, id_carta: int, ruta_pdf: str
    ) -> bool:
        """Registrar la entrega de las 3 copias físicas firmadas por el estudiante."""
        pass

    @abstractmethod
    def registrar_firma_decano_carta_compromiso(
        self, id_carta: int, firmado: bool
    ) -> bool:
        """Registrar la firma del Decana/o en las copias entregadas."""
        pass

    @abstractmethod
    def proponer_actividad(self, id_pr: int, descripcion: str) -> Actividad:
        pass

    @abstractmethod
    def revisar_actividad(
        self, id_act: int, id_pr: int, id_p_tutor_acad: int, aprobar: bool
    ) -> bool:
        """Permite al tutor académico validar o rechazar la tarea propuesta."""
        pass

    @abstractmethod
    def registrar_evaluacion_final(
        self, id_pr: int, tipo_formulario: str, datos_evaluacion: dict
    ) -> Formulario:
        """Completa de forma digital las rúbricas cuantitativas finales (Formularios 2 y 3)."""
        pass

    @abstractmethod
    def ejecutar_cierre_oficial(
        self, id_pr: int, id_p_coordinador: int
    ) -> bool:
        """Valida los formularios finales, aprueba el Formulario 1
        y da el cierre oficial a la práctica.
        """
        pass
