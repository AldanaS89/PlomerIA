from apscheduler.schedulers.background import BackgroundScheduler

from database import SessionLocal



scheduler = BackgroundScheduler()


# def start_scheduler():
#     """
#     Inicia el job de reasignación automática.
#     """

#     scheduler.add_job(
#         func=lambda: _procesar_reasignaciones(SessionLocal),
#         trigger="interval",
#         minutes=5,   # cada 5 minutos revisa
#         id="reasignacion_solicitudes",
#         replace_existing=True,
#     )

#     scheduler.start()
#     print("🟢 Scheduler de reasignaciones iniciado")