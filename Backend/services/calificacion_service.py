from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories import calificacion_repository, plomero_repository, solicitud_repository

def calificar_trabajo(
    db:           Session,
    id_solicitud: int,
    id_cliente:   int,
    estrellas:    int,
    comentario:   str | None = None,
) -> dict:

    # 1 — Verificar que la solicitud existe y está completada
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.estado.value != "completado":
        raise HTTPException(status_code=400, detail="Solo podés calificar trabajos completados")
    if solicitud.id_usuario != id_cliente:
        raise HTTPException(status_code=403, detail="No podés calificar este trabajo")

    # 2 — Verificar que no calificó antes
    if calificacion_repository.ya_califico(db, id_solicitud, id_cliente):
        raise HTTPException(status_code=400, detail="Ya calificaste este trabajo")

    # 3 — Crear la calificación
    calificacion_repository.crear(
        db, id_solicitud, solicitud.id_plomero, id_cliente, estrellas, comentario
    )

    # 4 — Actualizar promedio del plomero
    nuevo_promedio = calificacion_repository.calcular_promedio(db, solicitud.id_plomero)
    plomero_repository.actualizar_puntuacion(
        db, solicitud.id_plomero, nuevo_promedio,
        plomero_repository.buscar_por_id(db, solicitud.id_plomero).total_trabajos + 1
    )

    return {
        "mensaje":   "Calificación registrada correctamente",
        "promedio":  nuevo_promedio,
        "estrellas": estrellas,
    }