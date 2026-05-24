from pydantic import BaseModel, ConfigDict
from datetime import datetime


class MensajeCreate(BaseModel):
    id_solicitud: int
    texto: str


class MensajeResponse(BaseModel):
    id_mensaje: int
    id_solicitud: int
    emisor_id: int
    emisor_rol: str
    texto: str
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)