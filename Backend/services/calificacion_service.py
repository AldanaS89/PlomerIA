# services/calificacion_service.py
"""
Sistema de calificación bidireccional — PlomerIA.

FLUJO NORMAL:
  1. Plomero marca TERMINADO
     → solicitud pasa a PENDIENTE_CALIFICACION
     → se guarda fecha_vencimiento_calificacion = ahora + 72hs
     → al plomero se le muestra inmediatamente las estrellas para calificar al cliente
  2. Cliente tiene 72hs para calificar al plomero (con comentario opcional)
  3. Plomero tiene 72hs para calificar al cliente (solo estrellas, sin texto)
  4. Cuando LOS DOS calificaron → solicitud pasa a COMPLETADA
  5. Si alguno no califica antes del vencimiento → el scheduler registra
     5 estrellas automáticas y cierra la solicitud

PENALIZACIONES POR CANCELACIÓN:
  No son una resta directa. Son calificaciones automáticas del sistema
  que entran al promedio igual que una calificación real.

  ┌──────────────────────────┬──────────────────┬──────────────────────┐
  │ Tiempo al turno          │ Sin mensajería   │ Con mensajería       │
  ├──────────────────────────┼──────────────────┼──────────────────────┤
  │ Más de 24hs              │ 1 ⭐             │ 2 ⭐                │
  │ Menos de 24hs            │ 0.5 ⭐           │ 1.5 ⭐              │
  └──────────────────────────┴──────────────────┴──────────────────────┘

POLIMORFISMO:
  Las reglas son idénticas para cliente y plomero.
  Las funciones reciben rol_actor="cliente"|"plomero" y actúan en consecuencia
  sin duplicar lógica. La misma función registra, calcula y penaliza a ambos.

PROMEDIO:
  Arranca en 5.0 (cuenta como 1 trabajo base en el denominador).
  Suma al promedio: trabajos calificados + penalizaciones por cancelación.
  3 cancelaciones consecutivas → suspensión automática.
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
# CONSTANTES
# ─────────────────────────────────────────────

PEN_SIN_MSG_MAS_24H   = 1.0
PEN_SIN_MSG_MENOS_24H = 0.5
PEN_CON_MSG_MAS_24H   = 2.0
PEN_CON_MSG_MENOS_24H = 1.5

CANCELACIONES_PARA_SUSPENSION  = 3
HORAS_PARA_CALIFICAR           = 72   # plazo para calificar post-trabajo
HORAS_ALERTA_CALIFICACION      = 48   # cuándo mandar el recordatorio
ESTRELLAS_VENCIMIENTO          = 5.0  # automáticas si no califican a tiempo


# ─────────────────────────────────────────────
# HELPERS — penalización
# ─────────────────────────────────────────────

def _hubo_comunicacion(db: Session, id_solicitud: int) -> bool:
    mensajes = mensaje_repository.listar_por_solicitud(db, id_solicitud)
    return len(mensajes) > 0


def _horas_al_turno(solicitud) -> float | None:
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
    if horas is None or horas <= 24:
        return PEN_CON_MSG_MENOS_24H if hubo_msg else PEN_SIN_MSG_MENOS_24H
    return PEN_CON_MSG_MAS_24H if hubo_msg else PEN_SIN_MSG_MAS_24H


def _comentario_automatico(
    horas: float | None, hubo_msg: bool, rol_actor: str
) -> str:
    actor  = "El cliente" if rol_actor == "cliente" else "El profesional"
    tiempo = (
        "con mas de 24hs de anticipacion"    if horas and horas > 24
        else "con menos de 24hs de anticipacion" if horas is not None
        else "sin turno confirmado"
    )
    aviso = "habiendo avisado por mensajeria" if hubo_msg else "sin comunicacion previa"
    return f"Cancelacion — {actor} cancelo {tiempo}, {aviso}."


# ─────────────────────────────────────────────
# HELPERS — promedio (polimórfico)
# ─────────────────────────────────────────────

def _recalcular_promedio(
    db: Session, solicitud, rol_evaluado: str
) -> float:
    """
    Recalcula y persiste el promedio de quien fue evaluado.
    rol_evaluado == "plomero" → recalcula al plomero
    rol_evaluado == "cliente" → recalcula al cliente
    La lógica es idéntica para los dos actores.
    """
    if rol_evaluado == "plomero":
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


def _incrementar_cancelaciones(
    db: Session, id_actor: int, rol_actor: str
) -> None:
    """
    Incrementa cancelaciones_consecutivas y suspende al llegar a 3.
    Funciona igual para cliente y plomero — duck typing.
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
    Entra al promedio igual que una calificación real.
    Aplica las mismas reglas para cliente y plomero.
    Devuelve las estrellas registradas.
    """
    hubo_msg       = _hubo_comunicacion(db, solicitud.id_solicitud)
    horas          = _horas_al_turno(solicitud)
    estrellas_auto = _estrellas_automaticas(horas, hubo_msg)

    calificacion_repository.registrar_calificacion(
        db           = db,
        id_solicitud = solicitud.id_solicitud,
        id_plomero   = solicitud.id_plomero,
        id_cliente   = solicitud.id_usuario,
        autor_rol    = f"sistema_{rol_actor}",
        estrellas    = estrellas_auto,
        comentario   = _comentario_automatico(horas, hubo_msg, rol_actor),
    )

    # El penalizado es quien canceló
    _recalcular_promedio(db, solicitud, rol_actor)
    _incrementar_cancelaciones(db, id_actor, rol_actor)

    logger.info(
        "Penalizacion automatica: %s id=%s — %.1f estrellas (msg=%s, horas=%s)",
        rol_actor, id_actor, estrellas_auto, hubo_msg,
        round(horas, 1) if horas is not None else "sin turno",
    )

    return estrellas_auto


# ─────────────────────────────────────────────
# ACTIVAR PERÍODO DE CALIFICACIÓN
# ─────────────────────────────────────────────

def activar_periodo_calificacion(
    db: Session, id_solicitud: int
) -> None:
    """
    Llamado por solicitud_service cuando el plomero marca TERMINADO.
    Guarda la fecha de vencimiento (ahora + 72hs) en la solicitud.
    """
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        return

    solicitud.fecha_vencimiento_calificacion = (
        datetime.now() + timedelta(hours=HORAS_PARA_CALIFICAR)
    )
    db.commit()

    logger.info(
        "Periodo de calificacion activado para solicitud %s — vence %s",
        id_solicitud,
        solicitud.fecha_vencimiento_calificacion.strftime("%d/%m/%Y %H:%M"),
    )


# ─────────────────────────────────────────────
# CALIFICACIÓN REAL — función central polimórfica
# ─────────────────────────────────────────────

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
    estrellas:    float,
    comentario:   str | None = None,
) -> dict:
    """
    Función central de calificación — polimórfica.
    Misma lógica de validación para cliente y plomero.
    Solo cambia quién evalúa a quién:
      rol_autor="cliente" → evalúa al plomero
      rol_autor="plomero" → evalúa al cliente (solo estrellas, sin reseña)

    Si los dos calificaron → solicitud pasa a COMPLETADA.
    """
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if solicitud.estado != EstadoSolicitud.PENDIENTE_CALIFICACION:
        raise HTTPException(
            status_code=400,
            detail="Solo podes calificar trabajos pendientes de calificacion",
        )

    # Verificar que el autor pertenece a esta solicitud
    if rol_autor == "cliente" and solicitud.id_usuario != id_autor:
        raise HTTPException(status_code=403, detail="No podes calificar este trabajo")
    if rol_autor == "plomero" and solicitud.id_plomero != id_autor:
        raise HTTPException(status_code=403, detail="No podes calificar este trabajo")

    # Evitar doble calificación
    if calificacion_repository.ya_califico(db, id_solicitud, rol_autor):
        raise HTTPException(status_code=400, detail="Ya calificaste este trabajo")

    # El plomero no escribe reseña — solo estrellas
    comentario_final = None if rol_autor == "plomero" else comentario

    calificacion_repository.registrar_calificacion(
        db           = db,
        id_solicitud = id_solicitud,
        id_plomero   = solicitud.id_plomero,
        id_cliente   = solicitud.id_usuario,
        autor_rol    = rol_autor,
        estrellas    = estrellas,
        comentario   = comentario_final,
    )

    # El evaluado es el opuesto al autor
    rol_evaluado   = "plomero" if rol_autor == "cliente" else "cliente"
    nueva_puntuacion = _recalcular_promedio(db, solicitud, rol_evaluado)

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


# Alias para compatibilidad con el router actual
def registrar_calificacion_post_servicio(
    db:           Session,
    id_solicitud: int,
    id_cliente:   int,
    estrellas:    float,
    comentario:   str | None = None,
) -> dict:
    """
    Wrapper para la ruta del cliente — mantiene compatibilidad
    con el router existente sin duplicar lógica.
    """
    return registrar_calificacion(
        db           = db,
        id_solicitud = id_solicitud,
        id_autor     = id_cliente,
        rol_autor    = "cliente",
        estrellas    = estrellas,
        comentario   = comentario,
    )