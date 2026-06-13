def aplicar_qss_global(view) -> None:
    if hasattr(view, "setStyleSheet"):
        qss = """
        QPushButton {
            border-radius: 4px;
            padding: 5px 10px;
            font-weight: 500;
        }
        QPushButton {
            background-color: #2980b9;
            color: white;
            border: 1px solid #1f618d;
        }
        QPushButton:hover {
            background-color: #3498db;
        }
        /* Action buttons (primary actions: postular, aprobar, aceptar, guardar, publicar, descargar, subir, entrar, etc.) */
        QPushButton#btnAprobarOferta, QPushButton#btnAceptarPostulacion, QPushButton#btnPostularOferta,
        QPushButton#btnEnviarSolicitud, QPushButton#btnProponerActividad, QPushButton#btnGuardarActividad,
        QPushButton#btnAceptar, QPushButton#btnGuardar, QPushButton#btnPublicar, QPushButton#btnDescargarForm1,
        QPushButton#btnSubirForm1, QPushButton#btnSubirForm2, QPushButton#btnSubirForm3, QPushButton#btnDescargarForm2,
        QPushButton#btnDescargarForm3, QPushButton#btnEntrar {
            background-color: #2ecc71;
            border: 1px solid #27ae60;
            color: white;
        }
        QPushButton#btnAprobarOferta:hover, QPushButton#btnAceptarPostulacion:hover, QPushButton#btnPostularOferta:hover,
        QPushButton#btnEnviarSolicitud:hover, QPushButton#btnProponerActividad:hover, QPushButton#btnGuardarActividad:hover,
        QPushButton#btnAceptar:hover, QPushButton#btnGuardar:hover, QPushButton#btnPublicar:hover,
        QPushButton#btnDescargarForm1:hover, QPushButton#btnSubirForm1:hover, QPushButton#btnSubirForm2:hover,
        QPushButton#btnSubirForm3:hover, QPushButton#btnDescargarForm2:hover, QPushButton#btnDescargarForm3:hover,
        QPushButton#btnEntrar:hover {
            background-color: #27ae60;
        }
        /* Reject/close/cancel/baja buttons (alternatives) */
        QPushButton#btnRechazarOferta, QPushButton#btnRechazarPostulacion, QPushButton#btnNavCerrarSesion,
        QPushButton#btnCerrar, QPushButton#btnCerrarSesion, QPushButton#btnSalir, QPushButton#btnBaja,
        QPushButton#btnDarDeBaja, QPushButton#btnNavCerrarSesion_2 {
            background-color: #e74c3c;
            border: 1px solid #c0392b;
            color: white;
        }
        QPushButton#btnRechazarOferta:hover, QPushButton#btnRechazarPostulacion:hover, QPushButton#btnNavCerrarSesion:hover,
        QPushButton#btnCerrar:hover, QPushButton#btnCerrarSesion:hover, QPushButton#btnSalir:hover,
        QPushButton#btnBaja:hover, QPushButton#btnDarDeBaja:hover, QPushButton#btnNavCerrarSesion_2:hover {
            background-color: #c0392b;
        }
        /* Navigation / Neutral buttons */
        QPushButton#btnNavOfertas, QPushButton#btnNavPostulaciones, QPushButton#btnNavSolicitar, 
        QPushButton#btnNavBitacora, QPushButton#btnNavPublicar, QPushButton#btnNavHistorial, 
        QPushButton#btnNavTutores, QPushButton#btnVerTerna, QPushButton#btnVolverHistorial {
            background-color: #34495e;
            border: 1px solid #2c3e50;
            color: white;
        }
        QPushButton#btnNavOfertas:hover, QPushButton#btnNavPostulaciones:hover, QPushButton#btnNavSolicitar:hover, 
        QPushButton#btnNavBitacora:hover, QPushButton#btnNavPublicar:hover, QPushButton#btnNavHistorial:hover, 
        QPushButton#btnNavTutores:hover, QPushButton#btnVerTerna:hover, QPushButton#btnVolverHistorial:hover {
            background-color: #2c3e50;
        }
        """
        view.setStyleSheet(qss)
