from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.mensaje import MensajeCreate
from services import chat_service
from core.auth import get_usuario_actual

router = APIRouter(tags=["Chat"])


@router.post("/")
def enviar(
    datos: MensajeCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_usuario_actual)
):
    return chat_service.enviar_mensaje(
        db=db,
        id_solicitud=datos.id_solicitud,
        texto=datos.texto,
        emisor_id=user_id,
        emisor_rol="usuario"
    )


@router.get("/{id_solicitud}")
def obtener(id_solicitud: int, db: Session = Depends(get_db)):
    return chat_service.obtener_chat(db, id_solicitud)