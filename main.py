"""
Sistema de Gestión de Prácticas Preprofesionales (SGPP)

Punto de entrada principal del sistema.
"""

from src.utils.inicializador_db import inicializar_todos_los_dat_semilla


def main():
    """Punto de entrada principal del sistema."""
    print("Inicializando Base de Datos SGPP...")
    inicializar_todos_los_dat_semilla()
    print("[OK] Base de Datos SGPP inicializada correctamente.")


if __name__ == "__main__":
    main()
