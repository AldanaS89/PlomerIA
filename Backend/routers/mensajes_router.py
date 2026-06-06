from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.mensaje import MensajeCreate
from services import mensajeria_service
from core.auth import get_actor_actual

router = APIRouter(tags=["Mensajes"])


@router.post("/")
def enviar(
    datos: MensajeCreate,
    db: Session = Depends(get_db),
    actor: dict = Depends(get_actor_actual),
):
    # Envia un mensaje en el chat de una solicitud.
    # Solo funciona si la solicitud esta EN_PROGRESO o EN_CAMINO.
    # El rol se toma del token (usuario | plomero), no se asume.
    return mensajeria_service.enviar_mensaje(
        db=db,
        id_solicitud=datos.id_solicitud,
        texto=datos.texto,
        emisor_id=actor["id"],
        emisor_rol=actor["role"],
    )


@router.get("/{id_solicitud}")
def obtener(
    id_solicitud: int,
    db: Session = Depends(get_db),
    actor: dict = Depends(get_actor_actual),
):
    # Devuelve el historial de mensajes de una solicitud.
    return mensajeria_service.obtener_chat(db, id_solicitud)
