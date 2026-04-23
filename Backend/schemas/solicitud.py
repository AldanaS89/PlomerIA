# schemas/solicitud.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SolicitudCreate(BaseModel):
    id_plomero      : int
    descripcion_raw : str
    imagen_path     : Optional[str] = None
    video_path      : Optional[str] = None

class SolicitudResponse(BaseModel):
    id_solicitud    : int
    id_usuario      : int
    id_plomero      : Optional[int]
    descripcion_raw : str
    imagen_path     : Optional[str]
    video_path      : Optional[str]
    etiqueta_ia     : Optional[str]
    urgencia_ia     : Optional[str]
    presupuesto_min : Optional[float]
    presupuesto_max : Optional[float]
    estado          : str
    fecha           : datetime

    class Config:
        from_attributes = True