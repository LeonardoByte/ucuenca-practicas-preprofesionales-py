import inspect
from typing import Optional, Union

import pytest

from src.models import (
    EstadoCartaCompromiso,
    EstadoFirmaFormulario,
    EstadoPostulacion,
    EstadoValidacionActividad,
    RolUsuario,
    TipoFormulario,
)
from src.services.interfaces import (
    AdministradorMainServiceABC,
    AutenticacionServiceABC,
    CoordinadorMainServiceABC,
    EmpresaMainServiceABC,
    EstudianteMainServiceABC,
    LoginMainServiceABC,
    OfertaServiceABC,
    PostulacionServiceABC,
    PracticaServiceABC,
    TutorAcademicoMainServiceABC,
    TutorEmpresarialMainServiceABC,
)


@pytest.mark.parametrize(
    "interface_class",
    [
        AutenticacionServiceABC,
        OfertaServiceABC,
        PostulacionServiceABC,
        PracticaServiceABC,
        LoginMainServiceABC,
        AdministradorMainServiceABC,
        EstudianteMainServiceABC,
        CoordinadorMainServiceABC,
        EmpresaMainServiceABC,
        TutorAcademicoMainServiceABC,
        TutorEmpresarialMainServiceABC,
    ],
)
def test_interface_instantiation_raises_type_error(interface_class):
    """Comprueba que intentar instanciar interfaces abstractas lanza TypeError."""
    with pytest.raises(TypeError):
        interface_class()


def _check_annotation(parameter, expected_types):
    annotation = parameter.annotation
    if annotation == inspect.Parameter.empty:
        return False
    # Check union types like Optional[int] (which is Union[int, None])
    if getattr(annotation, "__origin__", None) is Union:
        args = annotation.__args__
        return any(t in expected_types for t in args)
    return annotation in expected_types


def test_autenticacion_service_signature():
    sig = inspect.signature(AutenticacionServiceABC.registrar_nuevo_perfil_sistema)
    assert _check_annotation(sig.parameters["rol"], [RolUsuario])


def test_postulacion_service_signature():
    sig_reg = inspect.signature(PostulacionServiceABC.registrar_postulacion)
    assert _check_annotation(sig_reg.parameters["id_p_coordinador"], [int, None, Optional[int]])

    sig_state = inspect.signature(PostulacionServiceABC.cambiar_estado)
    assert _check_annotation(sig_state.parameters["nuevo_estado"], [EstadoPostulacion])


def test_practica_service_signature():
    sig_eval = inspect.signature(PracticaServiceABC.evaluar_actividad)
    assert _check_annotation(sig_eval.parameters["estado"], [EstadoValidacionActividad])

    sig_form = inspect.signature(PracticaServiceABC.actualizar_formulario)
    assert _check_annotation(sig_form.parameters["tipo_formulario"], [TipoFormulario])
    assert _check_annotation(sig_form.parameters["estado_firma"], [EstadoFirmaFormulario])

    sig_carta = inspect.signature(PracticaServiceABC.registrar_entrega_carta_compromiso)
    assert _check_annotation(sig_carta.parameters["nuevo_estado"], [EstadoCartaCompromiso])

    # Debería poseer asignar_tutor_academico
    assert hasattr(PracticaServiceABC, "asignar_tutor_academico")
    sig_tutor = inspect.signature(PracticaServiceABC.asignar_tutor_academico)
    assert "id_p_tutor_acad" in sig_tutor.parameters

    # formalizar_practica no debe requerir id_p_tutor_acad
    sig_formalize = inspect.signature(PracticaServiceABC.formalizar_practica)
    assert "id_p_tutor_acad" not in sig_formalize.parameters


def test_administrador_main_service_signature():
    sig = inspect.signature(AdministradorMainServiceABC.crear_cuenta_usuario_sistema)
    assert _check_annotation(sig.parameters["rol"], [RolUsuario])


def test_estudiante_main_service_signature():
    sig = inspect.signature(EstudianteMainServiceABC.solicitar_postulacion)
    assert "id_p_coordinador" not in sig.parameters


def test_coordinador_main_service_signature():
    assert hasattr(CoordinadorMainServiceABC, "asignar_tutor_a_practica")
    sig = inspect.signature(CoordinadorMainServiceABC.asignar_tutor_a_practica)
    assert "id_p_tutor_acad" in sig.parameters


def test_empresa_main_service_signature():
    sig = inspect.signature(EmpresaMainServiceABC.seleccionar_candidato_ganador)
    assert "id_p_tutor_acad" not in sig.parameters


def test_tutor_academico_main_service_signature():
    sig_act = inspect.signature(TutorAcademicoMainServiceABC.evaluar_actividad_alumno)
    assert _check_annotation(sig_act.parameters["estado"], [EstadoValidacionActividad])

    sig_form = inspect.signature(TutorAcademicoMainServiceABC.registrar_evaluacion_formulario2)
    assert _check_annotation(sig_form.parameters["estado_de_firma"], [EstadoFirmaFormulario])
    assert "numero_formulario" not in sig_form.parameters


def test_tutor_empresarial_main_service_signature():
    sig_form = inspect.signature(TutorEmpresarialMainServiceABC.registrar_evaluacion_formulario3)
    assert _check_annotation(sig_form.parameters["estado_de_firma"], [EstadoFirmaFormulario])
    assert "numero_formulario" not in sig_form.parameters
