from abc import ABC, abstractmethod
from typing import Optional

from src.models import Oferta, Postulacion


class EmpresaMainServiceABC(ABC):

    @abstractmethod
    def registrar_oferta(self, id_e: int, descripcion_oferta: str, requisitos: str, fecha_de_publicacion: str, duracion: str, remuneracion: float) -> Optional[Oferta]:
        """Delega en OfertaService la creación de una nueva vacante en disco. Retorna None si falla."""
        pass

    @abstractmethod
    def visualizar_terna_recibida(self, id_terna: int) -> list[Postulacion]:
        """Usa PostulacionService para traer el listado histórico de candidatos de un bloque de despacho."""
        pass

    @abstractmethod
    def seleccionar_candidato_ganador(self, id_pos_aceptada: int, id_p_tutor_acad: int, id_p_tutor_emp: int, fecha_inicio: str, fecha_fin: str) -> bool:
        """Invoca a PracticaService para dar de alta la práctica, pasar la postulación a 'Aceptada' y rechazar las demás."""
        pass
