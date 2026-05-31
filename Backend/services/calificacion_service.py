# services/calificacion_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.solicitud import EstadoSolicitud
from repositories import (
    calificacion_repository,
    plomero_repository,
    solicitud_repository,
)


def registrar_calificacion_post_servicio(
    db:           Session,
    id_solicitud: int,
    id_cliente:   int,
    estrellas:    int,
    comentario:   str | None = None,
) -> dict:
    """
    Registra la calificación del cliente sobre el trabajo.
    Solo funciona cuando la solicitud está en PENDIENTE_CALIFICACION.
    Al calificar:
      - La solicitud pasa a COMPLETADA
      - Se recalcula la puntuación del plomero
      - Se incrementa total_trabajos del plomero
    """

    # 1 — Verificar que la solicitud existe y está pendiente de calificación
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada"
        )
    if solicitud.estado != EstadoSolicitud.PENDIENTE_CALIFICACION:
        raise HTTPException(
            status_code=400,
            detail="Solo podés calificar trabajos pendientes de calificación"
        )
    if solicitud.id_usuario != id_cliente:
        raise HTTPException(
            status_code=403,
            detail="No podés calificar este trabajo"
        )

    # 2 — Verificar que no calificó antes
    if calificacion_repository.cliente_ya_califico_trabajo(
        db, id_solicitud, id_cliente
    ):
        raise HTTPException(
            status_code=400,
            detail="Ya calificaste este trabajo"
        )

    # 3 — Registrar la calificación
    calificacion_repository.registrar_calificacion_de_trabajo(
        db           = db,
        id_solicitud = id_solicitud,
        id_plomero   = solicitud.id_plomero,
        id_cliente   = id_cliente,
        estrellas    = estrellas,
        comentario   = comentario,
    )

    # 4 — Pasar solicitud a COMPLETADA
    solicitud_repository.cambiar_estado(
        db, id_solicitud, EstadoSolicitud.COMPLETADA
    )

    # 5 — Recalcular puntuación e incrementar total_trabajos
    plomero = plomero_repository.buscar_por_id(db, solicitud.id_plomero)
    if plomero:
        trabajos_anteriores  = plomero.total_trabajos or 0  # 0 para plomeros nuevos

    # Promedio ponderado:
    # Los 5 puntos iniciales cuentan como 1 trabajo base
    # Entonces el denominador es: trabajos_reales + 1 (base) + 1 (nuevo) = trabajos + 2
        nueva_puntuacion = calificacion_repository.calcular_promedio_puntuacion(
            db,
            solicitud.id_plomero
        )

        plomero_repository.actualizar_puntuacion(
            db,
            solicitud.id_plomero,
            nueva_puntuacion,
            trabajos_anteriores + 1
        )

    return {
        "mensaje":   "Calificación registrada correctamente",
        "promedio":  round(nueva_puntuacion, 2),
        "estrellas": estrellas,
    }