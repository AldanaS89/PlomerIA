# services/scheduler_service.py
"""
Scheduler de PlomerIA — tareas en segundo plano.

Tareas activas:
  - Cada hora: cerrar calificaciones vencidas (48hs sin calificar → 5 estrellas automáticas)
  - Cada hora: enviar alerta de recordatorio cuando faltan 24hs para el vencimiento

Uso en main.py:
    from services.scheduler_service import iniciar_scheduler
    iniciar_scheduler()
"""

import logging
from datetime import datetime
from threading import Thread, Event
from time import sleep

from database import SessionLocal
from models.solicitud import EstadoSolicitud
from repositories import (
    solicitud_repository,
    calificacion_repository,
    plomero_repository,
    usuario_repository,
)
from services.calificacion_service import (
    ESTRELLAS_VENCIMIENTO,
    HORAS_ALERTA_CALIFICACION,
    _recalcular_promedio,
)

logger = logging.getLogger(__name__)

_stop_event = Event()
INTERVALO_SEGUNDOS = 3600   # cada 1 hora


# ─────────────────────────────────────────────
# TAREA: cerrar calificaciones vencidas
# ─────────────────────────────────────────────

def _cerrar_calificaciones_vencidas(db) -> int:
    """
    Busca solicitudes en PENDIENTE_CALIFICACION cuyo plazo venció.
    Para cada actor que no calificó, registra 5 estrellas automáticas.
    Cuando los dos están resueltos, cierra la solicitud como COMPLETADA.
    Devuelve la cantidad de solicitudes procesadas.
    """
    ahora = datetime.now()

    solicitudes_vencidas = (
        db.query(__import__("models.solicitud", fromlist=["Solicitud"]).Solicitud)
        .filter(
            __import__("models.solicitud", fromlist=["Solicitud"]).Solicitud.estado
            == EstadoSolicitud.PENDIENTE_CALIFICACION,
            __import__("models.solicitud", fromlist=["Solicitud"]).Solicitud.fecha_vencimiento_calificacion
            != None,
            __import__("models.solicitud", fromlist=["Solicitud"]).Solicitud.fecha_vencimiento_calificacion
            <= ahora,
        )
        .all()
    )

    procesadas = 0

    for solicitud in solicitudes_vencidas:
        try:
            _resolver_vencimiento(db, solicitud)
            procesadas += 1
        except Exception as e:
            logger.error(
                "Error procesando vencimiento solicitud %s: %s",
                solicitud.id_solicitud, e
            )

    return procesadas


def _resolver_vencimiento(db, solicitud) -> None:
    """
    Registra 5 estrellas automáticas para quien no calificó
    y cierra la solicitud.
    """
    cliente_califico = calificacion_repository.ya_califico(
        db, solicitud.id_solicitud, "cliente"
    )
    plomero_califico = calificacion_repository.ya_califico(
        db, solicitud.id_solicitud, "plomero"
    )

    if not cliente_califico:
        calificacion_repository.registrar_calificacion(
            db           = db,
            id_solicitud = solicitud.id_solicitud,
            id_plomero   = solicitud.id_plomero,
            id_cliente   = solicitud.id_usuario,
            autor_rol    = "sistema_vencimiento",
            estrellas    = ESTRELLAS_VENCIMIENTO,
            comentario   = "Calificacion automatica — el cliente no califico dentro del plazo de 72hs.",
        )
        _recalcular_promedio(db, solicitud, "plomero")
        logger.info(
            "Vencimiento: 5 estrellas automaticas al plomero %s (solicitud %s)",
            solicitud.id_plomero, solicitud.id_solicitud,
        )

    if not plomero_califico:
        calificacion_repository.registrar_calificacion(
            db           = db,
            id_solicitud = solicitud.id_solicitud,
            id_plomero   = solicitud.id_plomero,
            id_cliente   = solicitud.id_usuario,
            autor_rol    = "sistema_vencimiento",
            estrellas    = ESTRELLAS_VENCIMIENTO,
            comentario   = "Calificacion automatica — el plomero no califico dentro del plazo de 72hs.",
        )
        _recalcular_promedio(db, solicitud, "cliente")
        logger.info(
            "Vencimiento: 5 estrellas automaticas al cliente %s (solicitud %s)",
            solicitud.id_usuario, solicitud.id_solicitud,
        )

    solicitud_repository.cambiar_estado(
        db, solicitud.id_solicitud, EstadoSolicitud.COMPLETADA
    )
    logger.info("Solicitud %s cerrada por vencimiento de calificacion", solicitud.id_solicitud)


# ─────────────────────────────────────────────
# TAREA: alertas de recordatorio
# ─────────────────────────────────────────────

def _enviar_alertas_recordatorio(db) -> int:
    """
    Busca solicitudes en PENDIENTE_CALIFICACION que vencen en las próximas
    HORAS_ALERTA_CALIFICACION horas (48hs) y todavía no fueron alertadas.
    Registra la alerta para evitar duplicados.
    Devuelve la cantidad de alertas enviadas.
    """
    from datetime import timedelta
    ahora   = datetime.now()
    umbral  = ahora + timedelta(hours=HORAS_ALERTA_CALIFICACION)

    # Por ahora logueamos — cuando haya sistema de notificaciones push
    # esto se reemplaza por notificacion_service.enviar_alerta()
    from models.solicitud import Solicitud

    solicitudes = (
        db.query(Solicitud)
        .filter(
            Solicitud.estado == EstadoSolicitud.PENDIENTE_CALIFICACION,
            Solicitud.fecha_vencimiento_calificacion != None,
            Solicitud.fecha_vencimiento_calificacion >  ahora,
            Solicitud.fecha_vencimiento_calificacion <= umbral,
        )
        .all()
    )

    alertadas = 0

    for s in solicitudes:
        cliente_califico = calificacion_repository.ya_califico(db, s.id_solicitud, "cliente")
        plomero_califico = calificacion_repository.ya_califico(db, s.id_solicitud, "plomero")

        if not cliente_califico:
            logger.info(
                "ALERTA recordatorio → cliente %s: te quedan menos de 24hs para calificar (solicitud %s)",
                s.id_usuario, s.id_solicitud,
            )
            alertadas += 1

        if not plomero_califico:
            logger.info(
                "ALERTA recordatorio → plomero %s: te quedan menos de 24hs para calificar (solicitud %s)",
                s.id_plomero, s.id_solicitud,
            )
            alertadas += 1

    return alertadas


# ─────────────────────────────────────────────
# TAREA: limpiar notificaciones viejas
# ─────────────────────────────────────────────

DIAS_RETENCION_NOTIFICACIONES = 7


def _limpiar_notificaciones_viejas(db) -> int:
    """Borra notificaciones con más de 7 días para que la lista no crezca infinito."""
    from datetime import timedelta
    from repositories import notificacion_repository
    corte = datetime.utcnow() - timedelta(days=DIAS_RETENCION_NOTIFICACIONES)
    return notificacion_repository.eliminar_antiguas(db, corte)


# ─────────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────────

def _run_scheduler() -> None:
    logger.info("Scheduler iniciado — intervalo: %s segundos", INTERVALO_SEGUNDOS)

    while not _stop_event.is_set():
        db = SessionLocal()
        try:
            cerradas  = _cerrar_calificaciones_vencidas(db)
            alertadas = _enviar_alertas_recordatorio(db)
            limpiadas = _limpiar_notificaciones_viejas(db)

            if cerradas or alertadas or limpiadas:
                logger.info(
                    "Scheduler: %s cerradas, %s alertas, %s notificaciones viejas borradas",
                    cerradas, alertadas, limpiadas,
                )
        except Exception as e:
            logger.error("Error en scheduler: %s", e)
        finally:
            db.close()

        _stop_event.wait(timeout=INTERVALO_SEGUNDOS)

    logger.info("Scheduler detenido")


# ─────────────────────────────────────────────
# API PÚBLICA
# ─────────────────────────────────────────────

def iniciar_scheduler() -> None:
    """
    Inicia el scheduler en un hilo de background.
    Llamar desde main.py al arrancar la app.
    """
    t = Thread(target=_run_scheduler, daemon=True, name="plomeria-scheduler")
    t.start()
    logger.info("Scheduler thread iniciado")


def detener_scheduler() -> None:
    """Detiene el scheduler ordenadamente."""
    _stop_event.set()