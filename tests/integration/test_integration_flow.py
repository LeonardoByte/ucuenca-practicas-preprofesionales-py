import pickle
from pathlib import Path

from src.controllers import LoginController
from src.models import (
    Actividad,
    CartaCompromiso,
    Formulario,
    Oferta,
    Practica,
    SolicitudAutorizacion,
)


def test_login_flow(entorno_binario_temporal):
    """Test 1: Verify the login check against usuarios.dat.

    Ensures data is migrated from usuarios.json to usuarios.dat and
    authenticates different roles.
    """
    controller = LoginController()
    dat_path = Path("storage/db/usuarios.dat")

    # Perform a login which triggers the seed migration
    rol, user_id = controller.validar_credenciales("estudiante1", "pass123")
    assert rol == "Estudiante"
    assert user_id == 1

    # Verify usuarios.dat exists and is pickled
    assert dat_path.exists()
    with open(dat_path, "rb") as f:
        data = pickle.load(f)
    assert isinstance(data, list)
    user_names = [u.get("usuario") if isinstance(u, dict) else u.usuario for u in data]
    assert "estudiante1" in user_names

    # Test other roles
    assert controller.validar_credenciales("coordinador1", "pass123") == ("Coordinador", 2)
    assert controller.validar_credenciales("tutoracad1", "pass123") == ("Tutor Academico", 3)
    assert controller.validar_credenciales("tutoremp1", "pass123") == ("Tutor Empresarial", 4)
    assert controller.validar_credenciales("empresa1", "pass123") == ("Empresa", 10)

    # Test invalid credentials
    assert controller.validar_credenciales("estudiante1", "wrongpass") == (None, None)
    assert controller.validar_credenciales("nonexistent", "pass123") == (None, None)


def test_standard_practice_flow_and_closure_vigente(
    estudiante_repo,
    oferta_repo,
    postulacion_repo,
    practica_repo,
    formulario_repo,
    carta_compromiso_repo,
    estudiante_service,
    postulacion_service,
    practica_service,
):
    """Test 2: Verify the Standard Practice Flow (Vigente convenio).

    Covers eligibility, application, validation, terna grouping, selection,
    formalization (creating Formulario 1, no CartaCompromiso), tutor/activity
    flow (proposing and approving activities, completing Forms 2 & 3),
    and official closure.
    """
    # 1. Eligibility Check
    assert estudiante_service.verificar_elegibilidad(1) is True

    # 2. Create an Oferta for Tech Solutions (id_e=10 - convenio Vigente)
    oferta = Oferta(
        id_o="O1",
        id_e=10,
        descripcion_oferta="Python Developer",
        requisitos="6",
        fecha_de_publicacion="2026-05-25",
        duracion="320",
        remuneracion=150.0,
    )
    assert oferta_repo.guardar(oferta) is True

    # Verify Oferta was pickled
    assert Path("storage/db/ofertas.dat").exists()
    with open("storage/db/ofertas.dat", "rb") as f:
        pickled_ofertas = pickle.load(f)
    assert len(pickled_ofertas) > 0

    # 3. Student Applies
    assert postulacion_service.registrar_postulacion(id_p_estudiante=1, id_o="O1", id_e=10) is True

    # Verify postulation exists and is saved using pickle
    assert Path("storage/db/postulaciones.dat").exists()
    with open("storage/db/postulaciones.dat", "rb") as f:
        pickled_postulations = pickle.load(f)
    assert len(pickled_postulations) > 0

    postulaciones = postulacion_repo.listar_por_estudiante(1)
    assert len(postulaciones) == 1
    postulacion = postulaciones[0]
    assert postulacion.estado_de_postulacion == "Pendiente"
    id_pos = postulacion.id_pos

    # 4. Coordinator Validates
    assert (
        postulacion_service.validar_postulacion(
            id_pos=id_pos, id_p_coordinador=2, es_valida=True
        )
        is True
    )
    postulacion_updated = postulacion_repo.buscar_por_id(id_pos)
    assert postulacion_updated.estado_de_postulacion == "Validada"

    # 5. Coordinator groups into a terna
    terna = postulacion_service.enviar_postulaciones_a_empresa(id_o="O1", id_e=10, id_terna=100)
    assert len(terna) == 1
    assert terna[0].id_terna == 100

    # 6. Formalization (Company selects student)
    practica = practica_service.formalizar_practica_estandar(
        id_pos_aceptada=id_pos, id_p_tutor_acad=3, id_p_tutor_emp=4
    )
    assert isinstance(practica, Practica)
    assert practica.estado_de_practica == "Iniciada"
    id_pr = practica.id_pr

    # Verify postulation status is Aceptada
    postulacion_final = postulacion_repo.buscar_por_id(id_pos)
    assert postulacion_final.estado_de_postulacion == "Aceptada"

    # Verify student state is Activa
    estudiante = estudiante_repo.buscar_por_id(1)
    assert estudiante.estado_practica == "Activa"

    # Verify Formulario 1 is created with Presentado status
    formularios = formulario_repo.listar_formularios_por_practica(id_pr)
    assert len(formularios) == 1
    form_1 = formularios[0]
    assert form_1.tipo_formulario == "Formulario 1"
    assert form_1.estado_de_firma == "Presentado"

    # Verify CartaCompromiso is NOT created
    carta = carta_compromiso_repo.buscar_por_practica(id_pr)
    assert carta is None

    # 7. Tutor/Activity Flow
    actividad = practica_service.proponer_actividad(id_pr=id_pr, descripcion="Semana 1: Setup")
    assert isinstance(actividad, Actividad)
    assert actividad.descripcion_de_la_tarea == "Semana 1: Setup"
    assert actividad.estado_de_validacion == "Propuesta"

    assert practica_service.revisar_actividad(
        id_act=actividad.id_act, id_pr=id_pr, id_p_tutor_acad=3, aprobar=True
    ) is True

    # Complete evaluations (Formularios 2 and 3)
    form_2 = practica_service.registrar_evaluacion_final(
        id_pr=id_pr, tipo_formulario="Formulario 2", datos_evaluacion={"criterio1": 9.5}
    )
    assert isinstance(form_2, Formulario)
    assert form_2.tipo_formulario == "Formulario 2"
    assert form_2.estado_de_firma == "Completado"

    form_3 = practica_service.registrar_evaluacion_final(
        id_pr=id_pr, tipo_formulario="Formulario 3", datos_evaluacion={"desempeno": 10.0}
    )
    assert isinstance(form_3, Formulario)
    assert form_3.tipo_formulario == "Formulario 3"
    assert form_3.estado_de_firma == "Completado"

    # 8. Cierre Oficial
    assert practica_service.ejecutar_cierre_oficial(id_pr=id_pr, id_p_coordinador=2) is True

    # Verify Formulario 1 is now Aprobado
    formularios_finales = formulario_repo.listar_formularios_por_practica(id_pr)
    form_1_final = next(f for f in formularios_finales if f.tipo_formulario == "Formulario 1")
    assert form_1_final.estado_de_firma == "Aprobado"

    # Verify Practica is Aprobada
    practica_updated = practica_repo.buscar_por_id(id_pr)
    assert practica_updated.estado_de_practica == "Aprobada"

    # Verify student state is Finalizada
    estudiante_final = estudiante_repo.buscar_por_id(1)
    assert estudiante_final.estado_practica == "Finalizada"


def test_standard_practice_flow_and_closure_no_vigente(
    estudiante_repo,
    oferta_repo,
    postulacion_repo,
    practica_repo,
    formulario_repo,
    carta_compromiso_repo,
    estudiante_service,
    postulacion_service,
    practica_service,
):
    """Test 3: Verify the Standard Practice Flow (No Vigente convenio).

    Covers eligibility, application, validation, terna grouping, selection,
    formalization (creating Formulario 1 and CartaCompromiso in Pendiente),
    tutor/activity flow, and official closure validation (verifying that closure
    is blocked until CartaCompromiso is signed).
    """
    # 1. Eligibility Check
    assert estudiante_service.verificar_elegibilidad(1) is True

    # 2. Create an Oferta for Innovatech (id_e=11 - convenio No Vigente)
    oferta = Oferta(
        id_o="O2",
        id_e=11,
        descripcion_oferta="Frontend Developer",
        requisitos="6",
        fecha_de_publicacion="2026-05-25",
        duracion="320",
        remuneracion=150.0,
    )
    assert oferta_repo.guardar(oferta) is True

    # 3. Student Applies
    assert postulacion_service.registrar_postulacion(id_p_estudiante=1, id_o="O2", id_e=11) is True
    postulacion = postulacion_repo.listar_por_estudiante(1)[0]
    id_pos = postulacion.id_pos

    # 4. Coordinator Validates
    assert (
        postulacion_service.validar_postulacion(
            id_pos=id_pos, id_p_coordinador=2, es_valida=True
        )
        is True
    )

    # 5. Coordinator groups into a terna
    postulacion_service.enviar_postulaciones_a_empresa(id_o="O2", id_e=11, id_terna=101)

    # 6. Formalization
    practica = practica_service.formalizar_practica_estandar(
        id_pos_aceptada=id_pos, id_p_tutor_acad=3, id_p_tutor_emp=4
    )
    assert isinstance(practica, Practica)
    id_pr = practica.id_pr

    # Verify CartaCompromiso is created with status Pendiente
    carta = carta_compromiso_repo.buscar_por_practica(id_pr)
    assert isinstance(carta, CartaCompromiso)
    assert carta.estado == "Pendiente"

    # 7. Tutor/Activity Flow
    actividad = practica_service.proponer_actividad(id_pr=id_pr, descripcion="Semana 1: Layout")
    assert practica_service.revisar_actividad(
        id_act=actividad.id_act, id_pr=id_pr, id_p_tutor_acad=3, aprobar=True
    ) is True

    # Complete evaluations
    practica_service.registrar_evaluacion_final(
        id_pr=id_pr, tipo_formulario="Formulario 2", datos_evaluacion={"nota": 9.0}
    )
    practica_service.registrar_evaluacion_final(
        id_pr=id_pr, tipo_formulario="Formulario 3", datos_evaluacion={"nota": 9.5}
    )

    # 8. Cierre Oficial (Should fail because CartaCompromiso is not Firmada)
    assert practica_service.ejecutar_cierre_oficial(id_pr=id_pr, id_p_coordinador=2) is False

    # Student delivers physical copies
    assert practica_service.registrar_entrega_carta_compromiso(
        id_pr=id_pr, id_carta=carta.id_carta, ruta_pdf="storage/documents/carta.pdf"
    ) is True
    carta_updated = carta_compromiso_repo.buscar_por_id(carta.id_carta)
    assert carta_updated.estado == "Entregada"

    # Cierre Oficial should still fail (needs Decano's signature, i.e., "Firmada")
    assert practica_service.ejecutar_cierre_oficial(id_pr=id_pr, id_p_coordinador=2) is False

    # Decano signs CartaCompromiso
    assert practica_service.registrar_firma_decano_carta_compromiso(
        id_carta=carta.id_carta, firmado=True
    ) is True
    carta_signed = carta_compromiso_repo.buscar_por_id(carta.id_carta)
    assert carta_signed.estado == "Firmada"

    # Cierre Oficial should now succeed
    assert practica_service.ejecutar_cierre_oficial(id_pr=id_pr, id_p_coordinador=2) is True

    # Verify states
    practica_final = practica_repo.buscar_por_id(id_pr)
    assert practica_final.estado_de_practica == "Aprobada"


def test_own_company_flow(
    estudiante_repo,
    empresa_repo,
    oferta_repo,
    postulacion_repo,
    practica_repo,
    formulario_repo,
    solicitud_autorizacion_repo,
    estudiante_service,
    practica_service,
):
    """Test 4: Verify the Own-Company Flow.

    Covers student submitting SolicitudAutorizacion, Coordinator approving it,
    which automatically:
    - Approves the request.
    - Creates the company in empresas.dat.
    - Creates the offer.
    - Creates and validates the postulation (state Aceptada or Validada).
    - Formalizes the practice.
    - Creates Formulario 1.
    - Sets student state to Activa.
    """
    # 1. Student submits SolicitudAutorizacion
    solicitud = estudiante_service.registrar_solicitud_autorizacion(
        id_p_estudiante=1,
        nombre_empresa="Own Company LLC",
        detalles_empresa="Development of own project",
    )
    assert isinstance(solicitud, SolicitudAutorizacion)
    assert solicitud.nombre_empresa == "Own Company LLC"
    assert solicitud.estado_solicitud == "Pendiente"
    id_sol = solicitud.id_sol_aut

    # Verify it is saved in database file using pickle
    assert Path("storage/db/solicitudes_autorizacion.dat").exists()
    with open("storage/db/solicitudes_autorizacion.dat", "rb") as f:
        pickled_solicitudes = pickle.load(f)
    assert any(s.id_sol_aut == id_sol for s in pickled_solicitudes)

    # 2. Coordinator approves it assigning tutors
    assert practica_service.aprobar_solicitud_autorizacion(
        id_sol_aut=id_sol,
        id_p_coordinador=2,
        id_p_tutor_acad=3,
        id_p_tutor_emp=4,
        aprobar=True,
    ) is True

    # Verify SolicitudAutorizacion is Aprobada
    sol_updated = solicitud_autorizacion_repo.buscar_por_id(id_sol)
    assert sol_updated.estado_solicitud == "Aprobada"

    # Verify Empresa was created
    assert Path("storage/db/empresas.dat").exists()
    with open("storage/db/empresas.dat", "rb") as f:
        empresas = pickle.load(f)
    empresa_creada = next((e for e in empresas if e.nombre_empresa == "Own Company LLC"), None)
    assert empresa_creada is not None
    id_e_creada = empresa_creada.id_e

    # Verify Oferta was created
    with open("storage/db/ofertas.dat", "rb") as f:
        ofertas = pickle.load(f)
    ofertas_creadas = [o for o in ofertas if o.id_e == id_e_creada]
    assert len(ofertas_creadas) > 0

    # Verify Postulacion was created
    with open("storage/db/postulaciones.dat", "rb") as f:
        postulaciones = pickle.load(f)
    postulaciones_creadas = [
        p for p in postulaciones if p.id_p_estudiante == 1 and p.id_e == id_e_creada
    ]
    assert len(postulaciones_creadas) > 0
    postulacion_creada = postulaciones_creadas[0]
    assert postulacion_creada.estado_de_postulacion in ("Aceptada", "Validada")

    # Verify Practica was formalized
    with open("storage/db/practicas.dat", "rb") as f:
        practicas = pickle.load(f)
    practicas_creadas = [pr for pr in practicas if pr.id_pos == postulacion_creada.id_pos]
    assert len(practicas_creadas) == 1
    practica_creada = practicas_creadas[0]
    assert practica_creada.estado_de_practica == "Iniciada"
    assert practica_creada.id_p_tutor_acad == 3
    assert practica_creada.id_p_tutor_emp == 4

    # Verify Formulario 1 is created
    with open("storage/db/formularios.dat", "rb") as f:
        formularios = pickle.load(f)
    forms_creados = [form for form in formularios if form.id_pr == practica_creada.id_pr]
    assert len(forms_creados) == 1
    assert forms_creados[0].tipo_formulario == "Formulario 1"
    assert forms_creados[0].estado_de_firma == "Presentado"

    # Verify Student status is Activa
    estudiante = estudiante_repo.buscar_por_id(1)
    assert estudiante.estado_practica == "Activa"
