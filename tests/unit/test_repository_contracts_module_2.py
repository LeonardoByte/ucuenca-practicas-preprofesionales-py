# ruff: noqa: E402
"""Módulo 2: Tests unitarios de contratos e interfaces de persistencia.

Verifica por metaprogramación que todas las interfaces de los repositorios
del ecosistema heredan de la clase base abstracta RepositoryABC y que se comportan
como clases abstractas puras impidiendo su instanciación directa.
"""

import sys
from unittest.mock import MagicMock

# Intercept src.utils.serialization imports to decouple interface checks
# from concrete serialization modules belonging to Module 3.
sys.modules["src.utils.serialization"] = MagicMock()

import pytest

from src.repositories.interfaces import (
    ActividadRepositoryABC,
    AdministradorRepositoryABC,
    CartaCompromisoRepositoryABC,
    ConvenioRepositoryABC,
    CoordinadorRepositoryABC,
    EmpresaRepositoryABC,
    EstudianteRepositoryABC,
    FormularioRepositoryABC,
    OfertaRepositoryABC,
    PostulacionRepositoryABC,
    PracticaRepositoryABC,
    RepositoryABC,
    SolicitudAutorizacionRepositoryABC,
    SolicitudOficioRepositoryABC,
    TutorAcademicoRepositoryABC,
    TutorEmpresarialRepositoryABC,
    UsuarioRepositoryABC,
)


@pytest.mark.parametrize(
    "interface_class",
    [
        ActividadRepositoryABC,
        AdministradorRepositoryABC,
        CartaCompromisoRepositoryABC,
        ConvenioRepositoryABC,
        CoordinadorRepositoryABC,
        EmpresaRepositoryABC,
        EstudianteRepositoryABC,
        FormularioRepositoryABC,
        OfertaRepositoryABC,
        PostulacionRepositoryABC,
        PracticaRepositoryABC,
        SolicitudAutorizacionRepositoryABC,
        SolicitudOficioRepositoryABC,
        TutorAcademicoRepositoryABC,
        TutorEmpresarialRepositoryABC,
        UsuarioRepositoryABC,
    ],
)
def test_interface_inheritance_from_base(interface_class):
    """Verifica que todas las interfaces de repositorios especializadas hereden de RepositoryABC."""
    assert issubclass(interface_class, RepositoryABC)


@pytest.mark.parametrize(
    "abstract_class",
    [
        RepositoryABC,
        ActividadRepositoryABC,
        AdministradorRepositoryABC,
        CartaCompromisoRepositoryABC,
        ConvenioRepositoryABC,
        CoordinadorRepositoryABC,
        EmpresaRepositoryABC,
        EstudianteRepositoryABC,
        FormularioRepositoryABC,
        OfertaRepositoryABC,
        PostulacionRepositoryABC,
        PracticaRepositoryABC,
        SolicitudAutorizacionRepositoryABC,
        SolicitudOficioRepositoryABC,
        TutorAcademicoRepositoryABC,
        TutorEmpresarialRepositoryABC,
        UsuarioRepositoryABC,
    ],
)
def test_abstract_class_prevent_instantiation(abstract_class):
    """Verifica que intentar instanciar una clase abstracta levanta TypeError."""
    with pytest.raises(TypeError):
        abstract_class()
