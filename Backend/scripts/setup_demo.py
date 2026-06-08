"""
MAESTRO: deja la base lista para una demo desde cero.
Hace todo en orden: borra la base, carga plomeros ficticios, simula su
antigüedad (desde marzo 2026) y genera sus agendas.

⚠️ Borra cuentas creadas (vas a tener que re-registrar tu cliente/plomero de prueba).
Si solo querés reiniciar los TRABAJOS sin perder cuentas, usá reset_trabajos.py.

Uso: python scripts/setup_demo.py
"""
import os
import sys
import subprocess

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(script):
    print(f"\n===== {script} =====")
    subprocess.run([sys.executable, os.path.join("scripts", script)], cwd=BACKEND, check=True)


def main():
    print(">>> Setup completo de demo (borra todo y recarga ficticios)\n")
    run("reset_db.py")
    run("cargar_plomeros.py")
    run("simular_antiguedad.py")
    run("generar_agendas.py")
    print("\n✅ Listo: base limpia con plomeros ficticios, agendas y antigüedad.")


if __name__ == "__main__":
    main()
