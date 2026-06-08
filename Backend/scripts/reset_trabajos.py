"""
Reinicia SOLO el flujo de trabajo, para probar desde cero sin perder cuentas.

Borra: solicitudes, invitaciones, mensajes, notificaciones, calificaciones y
boletas. Libera las agendas (bloques ocupados). NO toca usuarios ni plomeros
(reales ni ficticios), así no hay que re-registrarse ni re-sembrar.

Además deja los contadores "como nuevos para una demo":
  - Plomeros FICTICIOS (los que están en plomeros_enriquecido.json):
    se les RESTAURA su puntuación y total_trabajos simulados del JSON,
    así conservan su trayectoria/ganancia simulada.
  - Plomeros y clientes que creaste VOS (no están en el JSON):
    arrancan de cero -> total_trabajos=0, puntuacion=5.0, sin sanciones.

Uso (desde Backend, con el venv activado):
    python scripts/reset_trabajos.py
"""
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal                      # noqa: E402
from models.mensaje import Mensaje                     # noqa: E402
from models.notificacion import Notificacion           # noqa: E402
from models.calificacion import Calificacion           # noqa: E402
from models.material import MaterialItem               # noqa: E402
from models.solicitud_plomero import SolicitudPlomero  # noqa: E402
from models.asignacion import Asignacion               # noqa: E402
from models.solicitud import Solicitud                 # noqa: E402
from models.bloqueHorario import BloqueHorario         # noqa: E402
from models.plomero import Plomero                     # noqa: E402
from models.usuario import Usuario                     # noqa: E402

# Mapa email -> datos simulados de los plomeros ficticios (si está el JSON)
JSON_FICTICIOS = Path(__file__).resolve().parent / "plomeros_enriquecido.json"


def _cargar_ficticios():
    """Devuelve {email: {puntuacion, total_trabajos}} de los ficticios del JSON."""
    if not JSON_FICTICIOS.exists():
        print(f"  ⚠ No se encontró {JSON_FICTICIOS.name}: no se pueden restaurar los ficticios.")
        return {}
    with open(JSON_FICTICIOS, encoding="utf-8") as f:
        data = json.load(f)
    return {
        d["email"]: {
            "puntuacion": d.get("puntuacion", 5.0),
            "total_trabajos": d.get("total_trabajos", 0),
        }
        for d in data if "email" in d
    }


def main():
    db = SessionLocal()
    try:
        # 1) Borrar el flujo de trabajo (hijos primero por si hay FKs)
        for M in [Mensaje, Notificacion, Calificacion, MaterialItem,
                  SolicitudPlomero, Asignacion, Solicitud]:
            n = db.query(M).delete()
            print(f"  {M.__name__}: {n} borrados")

        # 2) Liberar agendas (bloques marcados como ocupados)
        liberados = db.query(BloqueHorario).filter(
            BloqueHorario.ocupado == True  # noqa: E712
        ).update({BloqueHorario.ocupado: False})
        print(f"  Bloques liberados: {liberados}")

        # 3) Restaurar contadores
        ficticios = _cargar_ficticios()
        restaurados, reseteados = 0, 0
        for p in db.query(Plomero).all():
            sim = ficticios.get(p.email)
            if sim:  # ficticio -> restaurar trayectoria simulada
                p.puntuacion = sim["puntuacion"]
                p.total_trabajos = sim["total_trabajos"]
                restaurados += 1
            else:    # cuenta tuya -> arranca de cero
                p.puntuacion = 5.0
                p.total_trabajos = 0
                reseteados += 1
            p.cancelaciones_consecutivas = 0
            p.suspendido = False

        # Los clientes son todos "tuyos": arrancan de cero
        clientes = 0
        for u in db.query(Usuario).all():
            u.puntuacion = 5.0
            u.total_trabajos = 0
            u.cancelaciones_consecutivas = 0
            u.suspendido = False
            clientes += 1

        print(f"  Plomeros ficticios restaurados: {restaurados}")
        print(f"  Plomeros propios reseteados a 0: {reseteados}")
        print(f"  Clientes reseteados a 0: {clientes}")

        db.commit()
        print("\nReset completo. Cuentas conservadas; ficticios con su trayectoria, "
              "tus cuentas desde cero.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
