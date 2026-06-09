"""
Borra TODA la base (todas las tablas) y las recrea vacías.
⚠️ Se pierden TODAS las cuentas (clientes, plomeros reales y ficticios) y datos.
Después conviene recargar con cargar_plomeros.py / o usar setup_demo.py.

Uso: python scripts/reset_db.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models  # noqa: F401  (registra todas las tablas en Base)
from database import Base, engine  # noqa: E402


def main():
    print("Borrando TODAS las tablas...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Base reiniciada (vacía). Se perdieron cuentas y datos.")


if __name__ == "__main__":
    main()
