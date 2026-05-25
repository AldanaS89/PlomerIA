from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.mensaje import MensajeCreate
from services import mensajeria_service  
from core.auth import get_usuario_actual

router = APIRouter(tags=["Mensajes"])


@router.post("/")
def enviar(
    datos: MensajeCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_usuario_actual)
):
    """
    Envía un mensaje en el chat de una solicitud.
    Solo funciona si la solicitud está EN_PROGRESO.
    """
    return mensajeria_service.enviar_mensaje(
        db=db,
        id_solicitud=datos.id_solicitud,
        texto=datos.texto,
        emisor_id=user_id,
        emisor_rol="usuario"
    )


@router.get("/{id_solicitud}")
def obtener(
    id_solicitud: int,
    db: Session = Depends(get_db)
):
    """
    Devuelve el historial de mensajes de una solicitud.
    Útil para cargar el chat al abrir la pantalla.
    """
    return mensajeria_service.obtener_chat(db, id_solicitud)