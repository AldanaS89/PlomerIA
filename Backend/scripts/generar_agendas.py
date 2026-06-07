"""
Genera agendas simuladas para los plomeros que no tienen una.
Cada plomero queda con algunos días/franjas disponibles y otros no,
de forma determinística (misma agenda siempre por id).

Uso (desde la carpeta Backend, con el venv activado):
    python scripts/generar_agendas.py
"""
import os
import sys
import random

# Permite ejecutar el script desde Backend/ importando los módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal          # noqa: E402
from models.plomero import Plomero         # noqa: E402

DIAS    = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
FRANJAS = ["manana", "tarde", "noche"]


def generar_agenda(seed: int) -> dict:
    rnd = random.Random(seed)
    dias_trabaja = rnd.sample(DIAS, rnd.randint(4, 6))
    ag = {}
    for d in DIAS:
        for f in FRANJAS:
            if d in dias_trabaja:
                disp = (f != "noche" or rnd.random() < 0.4) and rnd.random() < 0.8
            else:
                disp = False
            if disp:
                ag[f"{d}_{f}"] = True
    # Asegurar al menos algunos slots disponibles
    if sum(1 for v in ag.values() if v) < 3:
        for d in dias_trabaja[:2]:
            ag[f"{d}_manana"] = True
    return ag


def main():
    db = SessionLocal()
    try:
        plomeros = db.query(Plomero).all()
        actualizados = 0
        for p in plomeros:
            vacia = not p.agenda or len(p.agenda) == 0
            if not vacia:
                continue
            p.agenda = generar_agenda(p.id_plomero)
            actualizados += 1
        db.commit()
        print(f"Agendas generadas: {actualizados} / {len(plomeros)} plomeros")
    finally:
        db.close()


if __name__ == "__main__":
    main()
