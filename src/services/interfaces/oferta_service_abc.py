from abc import ABC, abstractmethod
from typing import Optional

from src.models.empresa import Oferta


class OfertaServiceABC(ABC):
    @abstractmethod
    def crear_oferta(
        self,
        id_e: int,
        descripcion: str,
        requisitos: str,
        fecha_de_publicacion: str,
        duracion: str,
        remuneracion: float,
    ) -> Optional[Oferta]:
        """Registra una nueva vacante asociada a una empresa específica."""
        pass

    @abstractmethod
    def buscar_oferta_por_id(self, id_o: int) -> Optional[Oferta]:
        """Recupera una oferta mediante su identificador único simple."""
        pass

    @abstractmethod
    def listar_todas_las_ofertas(self) -> list[Oferta]:
        """Retorna el catálogo global de vacantes registradas en el sistema."""
        pass
