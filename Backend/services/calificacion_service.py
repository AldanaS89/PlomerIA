# services/calificacion_service.py
"""
Sistema de calificación bidireccional para PlomerIA.

Flujo normal:
  1. El plomero marca TERMINADO → solicitud pasa a PENDIENTE_CALIFICACION
  2. Ambos actores pueden calificar mientras el estado sea PENDIENTE_CALIFICACION
  3. Cuando LOS DOS calificaron → solicitud pasa a COMPLETADA

Penalizaciones por cancelación (aplica igual para cliente y plomero):
  La penalización NO es una resta directa de puntos.
  Es una calificación automática que el SISTEMA registra y entra
  al promedio exactamente igual que una calificación real de otro usuario.

  Tabla de calificaciones automáticas:
  ┌──────────────────────────┬──────────────────┬──────────────────────┐
  │ Tiempo al turno          │ Sin mensajería   │ Con mensajería       │
  ├──────────────────────────┼──────────────────┼──────────────────────┤
  │ Más de 24hs              │ 1 estrella       │ 2 estrellas          │
  │ Menos de 24hs            │ 0.5 estrellas    │ 1.5 estrellas        │
  └──────────────────────────┴──────────────────┴──────────────────────┘

  Comunicarse antes de cancelar mejora la calificación automática
  porque demuestra responsabilidad.

  El promedio base arranca en 5 (cuenta como 1 trabajo base).
  Ejemplo: 3 trabajos reales + 1 cancelación sin aviso a menos de 24hs:
  → (5_base + 5 + 4 + 3 + 0.5) / 5 = 3.5

  3 cancelaciones consecutivas → suspensión automática.
  El contador se resetea con cada trabajo completado exitosamente.
"""

import logging
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.solicitud import EstadoSolicitud
from models.plomero import Plomero
from repositories import (
    calificacion_repository,
    plomero_repository,
    solicitud_repository,
    usuario_repository,
    mensaje_repository,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# CONSTANTES — calificación automática por cancelación
# ─────────────────────────────────────────────

PEN_SIN_MSG_MAS_24H   = 1.0   # sin aviso, canceló con más de 24hs
PEN_SIN_MSG_MENOS_24H = 0.5   # sin aviso, canceló con menos de 24hs
PEN_CON_MSG_MAS_24H   = 2.0   # avisó, canceló con más de 24hs
PEN_CON_MSG_MENOS_24H = 1.5   # avisó, canceló con menos de 24hs

CANCELACIONES_PARA_SUSPENSION = 3


# ─────────────────────────────────────────────
# HELPERS DE PENALIZACIÓN
# ─────────────────────────────────────────────

def _hubo_comunicacion(db: Session, id_solicitud: int) -> bool:
    mensajes = mensaje_repository.listar_por_solicitud(db, id_solicitud)
    return len(mensajes) > 0


def _horas_al_turno(solicitud) -> float | None:
    """
    Horas que faltan hasta el turno. Usa fecha_trabajo si existe,
    sino parsea turno_solicitado. Devuelve None si no hay turno.
    """
    if solicitud.fecha_trabajo:
        return (solicitud.fecha_trabajo - datetime.now()).total_seconds() / 3600

    if solicitud.turno_solicitado:
        try:
            partes = solicitud.turno_solicitado.split("_")
            if len(partes) >= 3:
                IDX = {
                    "Lun": 0, "Mar": 1, "Mie": 2,
                    "Jue": 3, "Vie": 4, "Sab": 5, "Dom": 6,
                }
                dia_idx  = IDX.get(partes[0], 0)
                hora     = int(partes[2])
                hoy      = datetime.now()
                diff     = (dia_idx - hoy.weekday()) % 7
                turno_dt = hoy.replace(hour=hora, minute=0, second=0, microsecond=0)
                turno_dt += timedelta(days=diff if diff > 0 else 7)
                return (turno_dt - hoy).total_seconds() / 3600
        except Exception:
            pass

    return None


def _estrellas_automaticas(horas: float | None, hubo_msg: bool) -> float:
    """
    Determina las estrellas de la calificación automática.
    Sin turno asignado aplica la variante de menos de 24hs por precaución.
    """
    if horas is None or horas <= 24:
        return PEN_CON_MSG_MENOS_24H if hubo_msg else PEN_SIN_MSG_MENOS_24H
    return PEN_CON_MSG_MAS_24H if hubo_msg else PEN_SIN_MSG_MAS_24H


def _comentario_automatico(
    horas: float | None, hubo_msg: bool, rol_actor: str
) -> str:
    actor  = "El cliente" if rol_actor == "cliente" else "El profesional"
    tiempo = (
        "con más de 24hs de anticipación"   if horas and horas > 24
        else "con menos de 24hs de anticipación" if horas is not None
        else "sin turno confirmado"
    )
    aviso  = "habiendo avisado por mensajería" if hubo_msg else "sin comunicación previa"
    return f"Cancelación — {actor} canceló {tiempo}, {aviso}."


# ─────────────────────────────────────────────
# PENALIZACIÓN POR CANCELACIÓN
# ─────────────────────────────────────────────

def penalizar_por_cancelacion(
    db:        Session,
    solicitud,
    id_actor:  int,
    rol_actor: str,    # "cliente" | "plomero"
) -> float:
    """
    Registra una calificación automática del sistema por cancelación.
    Entra al promedio igual que una calificación real de otro usuario.
    Aplica igual para cliente y para plomero.
    Devuelve las estrellas registradas para informar al frontend.
    """
    hubo_msg      = _hubo_comunicacion(db, solicitud.id_solicitud)
    horas         = _horas_al_turno(solicitud)
    estrellas_auto = _estrellas_automaticas(horas, hubo_msg)

    # autor_rol con prefijo "sistema_" para distinguir de calificaciones reales
    calificacion_repository.registrar_calificacion(
        db           = db,
        id_solicitud = solicitud.id_solicitud,
        id_plomero   = solicitud.id_plomero,
        id_cliente   = solicitud.id_usuario,
        autor_rol    = f"sistema_{rol_actor}",
        estrellas    = estrellas_auto,
        comentario   = _comentario_automatico(horas, hubo_msg, rol_actor),
    )

    # Recalcular promedio del penalizado (la calificación ya fue insertada)
    _recalcular_promedio_penalizado(db, solicitud, rol_actor)

    # Controlar suspensión
    _incrementar_cancelaciones(db, id_actor, rol_actor)

    logger.info(
        "Penalizacion automatica: %s id=%s — %.1f estrellas (msg=%s, horas=%s)",
        rol_actor, id_actor, estrellas_auto, hubo_msg,
        round(horas, 1) if horas is not None else "sin turno",
    )

    return estrellas_auto


def _recalcular_promedio_penalizado(
    db: Session, solicitud, rol_actor: str
) -> None:
    """
    Recalcula el promedio del actor penalizado incluyendo la calificación
    automática que acaba de registrarse. La penalización cuenta como
    trabajo en el denominador para que impacte realmente en el promedio.
    """
    if rol_actor == "cliente":
        nueva   = calificacion_repository.calcular_promedio_cliente(
            db, solicitud.id_usuario
        )
        cliente = usuario_repository.buscar_por_id(db, solicitud.id_usuario)
        if cliente:
            cliente.puntuacion     = nueva
            cliente.total_trabajos = (cliente.total_trabajos or 0) + 1
            db.commit()
    else:
        nueva   = calificacion_repository.calcular_promedio_plomero(
            db, solicitud.id_plomero
        )
        plomero = plomero_repository.buscar_por_id(db, solicitud.id_plomero)
        if plomero:
            plomero_repository.actualizar_puntuacion(
                db, solicitud.id_plomero, nueva,
                (plomero.total_trabajos or 0) + 1,
            )


def _incrementar_cancelaciones(
    db: Session, id_actor: int, rol_actor: str
) -> None:
    """
    Incrementa cancelaciones_consecutivas y suspende al llegar a 3.
    Funciona igual para cliente y plomero (duck typing).
    """
    persona = (
        usuario_repository.buscar_por_id(db, id_actor)
        if rol_actor == "cliente"
        else plomero_repository.buscar_por_id(db, id_actor)
    )
    if not persona:
        return

    persona.cancelaciones_consecutivas = (
        persona.cancelaciones_consecutivas or 0
    ) + 1

    if persona.cancelaciones_consecutivas >= CANCELACIONES_PARA_SUSPENSION:
        if isinstance(persona, Plomero):
            persona.disponible_ahora = False
        persona.suspendido = True
        logger.warning(
            "%s id=%s suspendido tras %s cancelaciones consecutivas",
            type(persona).__name__, id_actor,
            persona.cancelaciones_consecutivas,
        )

    db.commit()


def resetear_cancelaciones(db: Session, persona) -> None:
    """Resetea el contador al completar un trabajo exitosamente."""
    persona.cancelaciones_consecutivas = 0
    db.commit()


# ─────────────────────────────────────────────
# CALIFICACIÓN REAL — función central polimórfica
# ─────────────────────────────────────────────

def _actualizar_puntuacion_evaluado(
    db: Session, solicitud, autor_rol: str
) -> float:
    """
    Recalcula y persiste la puntuación de quien fue evaluado.
    autor_rol == "cliente"  → evaluado es el plomero
    autor_rol == "plomero"  → evaluado es el cliente
    """
    if autor_rol == "cliente":
        nueva   = calificacion_repository.calcular_promedio_plomero(
            db, solicitud.id_plomero
        )
        plomero = plomero_repository.buscar_por_id(db, solicitud.id_plomero)
        if plomero:
            plomero_repository.actualizar_puntuacion(
                db, solicitud.id_plomero, nueva,
                (plomero.total_trabajos or 0) + 1,
            )
    else:
        nueva   = calificacion_repository.calcular_promedio_cliente(
            db, solicitud.id_usuario
        )
        cliente = usuario_repository.buscar_por_id(db, solicitud.id_usuario)
        if cliente:
            cliente.puntuacion     = nueva
            cliente.total_trabajos = (cliente.total_trabajos or 0) + 1
            db.commit()

    return nueva


def _ambos_calificaron(db: Session, id_solicitud: int) -> bool:
    return (
        calificacion_repository.ya_califico(db, id_solicitud, "cliente")
        and
        calificacion_repository.ya_califico(db, id_solicitud, "plomero")
    )


def registrar_calificacion(
    db:           Session,
    id_solicitud: int,
    id_autor:     int,
    rol_autor:    str,          # "cliente" | "plomero"
    estrellas:    int,
    comentario:   str | None = None,
) -> dict:
    """
    Función central de calificación. Funciona igual para cliente y plomero —
    solo cambia quién evalúa a quién. La lógica de validación es idéntica.
    """
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if solicitud.estado != EstadoSolicitud.PENDIENTE_CALIFICACION:
        raise HTTPException(
            status_code=400,
            detail="Solo podés calificar trabajos pendientes de calificación",
        )

    if rol_autor == "cliente" and solicitud.id_usuario != id_autor:
        raise HTTPException(status_code=403, detail="No podés calificar este trabajo")
    if rol_autor == "plomero" and solicitud.id_plomero != id_autor:
        raise HTTPException(status_code=403, detail="No podés calificar este trabajo")

    if calificacion_repository.ya_califico(db, id_solicitud, rol_autor):
        raise HTTPException(status_code=400, detail="Ya calificaste este trabajo")

    calificacion_repository.registrar_calificacion(
        db           = db,
        id_solicitud = id_solicitud,
        id_plomero   = solicitud.id_plomero,
        id_cliente   = solicitud.id_usuario,
        autor_rol    = rol_autor,
        estrellas    = estrellas,
        comentario   = comentario,
    )

    nueva_puntuacion = _actualizar_puntuacion_evaluado(db, solicitud, rol_autor)

    if _ambos_calificaron(db, id_solicitud):
        solicitud_repository.cambiar_estado(
            db, id_solicitud, EstadoSolicitud.COMPLETADA
        )
        estado_resultante = "completada"
    else:
        estado_resultante = "pendiente_calificacion"

    evaluado = "el plomero" if rol_autor == "cliente" else "el cliente"
    return {
        "mensaje":           f"Calificacion de {evaluado} registrada correctamente",
        "promedio_evaluado": round(nueva_puntuacion, 2),
        "estrellas":         estrellas,
        "estado_solicitud":  estado_resultante,
        "ambos_calificaron": estado_resultante == "completada",
    }