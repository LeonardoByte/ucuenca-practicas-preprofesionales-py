from abc import ABC, abstractmethod
from typing import Optional

from src.models import (
    Convenio,
    Oferta,
    Postulacion,
    Practica,
    TutorEmpresarial,
)


class EmpresaMainServiceABC(ABC):
    @abstractmethod
    def registrar_oferta(
        self,
        id_e: int,
        descripcion_oferta: str,
        requisitos: str,
        fecha_de_publicacion: str,
        duracion: str,
        remuneracion: float,
    ) -> Optional[Oferta]:
        """
        Delega en OfertaService la creación de una nueva vacante en disco.
        Retorna None si falla.
        """
        pass

    @abstractmethod
    def visualizar_terna_recibida(self, id_terna: int) -> list[Postulacion]:
        """
        Usa PostulacionService para traer el listado histórico de
        candidatos de un bloque de despacho.
        """
        pass

    @abstractmethod
    def seleccionar_candidato_ganador(
        self, id_pos_aceptada: int, id_p_tutor_emp: int, fecha_inicio: str, fecha_fin: str
    ) -> bool:
        """
        Invoca a PracticaService para dar de alta la práctica, pasar la
        postulación a 'Aceptada' y rechazar las demás.
        """
        pass

    @abstractmethod
    def listar_mis_ofertas_publicadas(self, id_e: int) -> list[Oferta]:
        """Usa OfertaService para jalar el catálogo completo filtrando funcionalmente
        por el ID de esta empresa.
        """
        pass

    @abstractmethod
    def crear_convenio_empresa(
        self, id_e: int, fecha_firma: str, fecha_vencimiento: str
    ) -> Optional[Convenio]:
        """Registra un nuevo convenio para la empresa."""
        pass

    @abstractmethod
    def obtener_convenios_empresa(self, id_e: int) -> list[Convenio]:
        """Obtiene todos los convenios registrados por la empresa."""
        pass

    @abstractmethod
    def obtener_tutores_de_empresa(self, id_e: int) -> list[TutorEmpresarial]:
        """Lista la planilla de personal empresarial disponible para tutorías."""
        pass

    @abstractmethod
    def obtener_ofertas_activas_empresa(self, id_e: int) -> list[Oferta]:
        """Lista las ofertas de la empresa que no están vinculadas a prácticas en curso."""
        pass

    @abstractmethod
    def obtener_historial_ofertas_empresa(self, id_e: int) -> list[Oferta]:
        """Lista las ofertas históricas de la empresa vinculadas a prácticas."""
        pass

    @abstractmethod
    def obtener_practicas_activas_empresa(self, id_e: int) -> list[Practica]:
        """Lista las prácticas activas asociadas a la empresa."""
        pass

    @abstractmethod
    def obtener_historial_practicas_empresa(self, id_e: int) -> list[Practica]:
        """Lista el historial de prácticas culminadas de la empresa."""
        pass
