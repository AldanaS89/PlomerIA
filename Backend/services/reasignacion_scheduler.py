from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from database import SessionLocal
from models.solicitud import Solicitud, EstadoSolicitud
from services.solicitud_service import _procesar_reasignaciones


scheduler = BackgroundScheduler()


# ─────────────────────────────────────────────
# JOB PRINCIPAL
# ─────────────────────────────────────────────

def job_reasignacion():
    db = SessionLocal()

    try:
        ahora = datetime.now()

        solicitudes = db.query(Solicitud).filter(
            Solicitud.estado.in_([
                EstadoSolicitud.PENDIENTE,
                EstadoSolicitud.REASIGNACION_PENDIENTE
            ])
        ).all()

        for s in solicitudes:

            # si nunca envió o pasaron 30 min → reintento
            if not s.fecha_ultimo_envio:
                continue

            if ahora - s.fecha_ultimo_envio < timedelta(minutes=30):
                continue

            _procesar_reasignaciones(db, s)

    finally:
        db.close()


# ─────────────────────────────────────────────
# START SCHEDULER
# ─────────────────────────────────────────────

def start_scheduler():
    scheduler.add_job(
        job_reasignacion,
        "interval",
        minutes=5,   # corre cada 5 min
        max_instances=1
    )
    scheduler.start()