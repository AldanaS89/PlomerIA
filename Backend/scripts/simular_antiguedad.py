"""
Backdatea fecha_registro de los plomeros (los ficticios) para simular que
ya venían trabajando, PERO nunca antes del lanzamiento de la app (marzo 2026).
Más trabajos => se registró más cerca del lanzamiento (más antiguo).
Determinístico por id.

Uso (desde Backend, con el venv activado):
    python scripts/simular_antiguedad.py
"""
import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal          # noqa: E402
from models.plomero import Plomero         # noqa: E402

# La app se lanzó en marzo 2026: ningún plomero puede ser anterior a esto.
LANZAMIENTO = datetime(2026, 3, 1)


def main():
    db = SessionLocal()
    try:
        plomeros = db.query(Plomero).all()
        ahora = datetime.now()
        dias_disponibles = max(1, (ahora - LANZAMIENTO).days)
        actualizados = 0
        for p in plomeros:
            trabajos = p.total_trabajos or 0
            if trabajos < 5:           # solo ficticios con trayectoria
                continue
            rnd = random.Random(p.id_plomero)
            # Más trabajos -> menor offset -> más cerca del lanzamiento (más antiguo)
            fraccion = min(1.0, trabajos / 200.0)
            offset = int((1 - fraccion) * dias_disponibles * rnd.uniform(0.4, 1.0))
            fecha = LANZAMIENTO + timedelta(days=offset)
            if fecha > ahora:
                fecha = ahora
            p.fecha_registro = fecha
            actualizados += 1
        db.commit()
        print(f"Antiguedad simulada (desde {LANZAMIENTO.date()}) en {actualizados} / {len(plomeros)} plomeros")
    finally:
        db.close()


if __name__ == "__main__":
    main()
