from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.auth import get_usuario_actual
from database import get_db
from services import calificacion_service


router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"])

@router.post("/{id_solicitud}")
def calificar(
    id_solicitud: int,
    estrellas: int,
    comentario: Optional[str] = None,
    db: Session = Depends(get_db),
    id_cliente: int = Depends(get_usuario_actual)
):
    return calificacion_service.calificar_trabajo(db, id_solicitud, id_cliente, estrellas, comentario)