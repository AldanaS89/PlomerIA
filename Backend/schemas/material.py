from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class MaterialCreate(BaseModel):
    descripcion: str
    cantidad: float = 1.0
    precio: float = 0.0


class MaterialResponse(BaseModel):
    id_item: int
    id_solicitud: int
    descripcion: str
    cantidad: float
    precio: float
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)
