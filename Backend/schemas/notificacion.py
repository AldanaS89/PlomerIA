from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class NotificacionResponse(BaseModel):
    id_notificacion: int
    destinatario_id: int
    destinatario_rol: str
    tipo: str
    titulo: str
    mensaje: str
    id_solicitud: Optional[int] = None
    leida: bool
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)
