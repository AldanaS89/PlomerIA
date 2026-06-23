# routers/calificaciones_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.calificacion import CalificacionRequest
from core.auth import get_usuario_actual, get_plomero_actual
from database import get_db
from services import calificacion_service
from repositories import solicitud_repository
from models.solicitud import EstadoSolicitud

router = APIRouter(tags=["Calificaciones"])


@router.post("/{id_solicitud}")
def calificar(
    id_solicitud: int,
    datos:        CalificacionRequest,
    db:           Session = Depends(get_db),
    id_cliente:   int     = Depends(get_usuario_actual),
):
    """
    El cliente califica el trabajo completado.
    Solo funciona si la solicitud está en PENDIENTE_CALIFICACION.
    Al calificar la solicitud pasa a COMPLETADA y se actualiza
    la puntuación y total_trabajos del plomero.
    """
    return calificacion_service.registrar_calificacion_post_servicio(
        db           = db,
        id_solicitud = id_solicitud,
        id_cliente   = id_cliente,
        estrellas    = datos.estrellas,
        comentario   = datos.comentario,
    )


@router.post("/plomero/{id_solicitud}")
def calificar_cliente(
    id_solicitud: int,
    datos:        CalificacionRequest,
    db:           Session = Depends(get_db),
    id_plomero:   int     = Depends(get_plomero_actual),
):
    """
    El plomero califica al cliente (solo estrellas, sin reseña).
    Misma lógica polimórfica que la calificación del cliente.
    Cuando ambos calificaron, la solicitud pasa a COMPLETADA.
    """
    return calificacion_service.registrar_calificacion(
        db           = db,
        id_solicitud = id_solicitud,
        id_autor     = id_plomero,
        rol_autor    = "plomero",
        estrellas    = datos.estrellas,
        comentario   = None,
    )


@router.get("/pendientes")
def calificaciones_pendientes(
    db:         Session = Depends(get_db),
    id_cliente: int     = Depends(get_usuario_actual),
):
    """
    Devuelve las solicitudes del cliente que están en
    PENDIENTE_CALIFICACION. El frontend usa esto para
    mostrar el badge de calificación pendiente.
    """
    solicitudes = solicitud_repository.listar_por_usuario(db, id_cliente)
    pendientes = [
        s for s in solicitudes
        if s.estado == EstadoSolicitud.PENDIENTE_CALIFICACION
    ]
    return {
        "cantidad": len(pendientes),
        "solicitudes": [
            {
                "id_solicitud": s.id_solicitud,
                "id_plomero":   s.id_plomero,
                "descripcion":  s.descripcion_raw,
                "fecha":        s.fecha.isoformat() if s.fecha else None,
            }
            for s in pendientes
        ]
    }