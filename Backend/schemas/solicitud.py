# schemas/solicitud.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SolicitudCreate(BaseModel):
    id_plomero      : Optional[int] = None
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

    @classmethod
    def from_orm_obj(cls, s):
        return cls(
            id_solicitud=s.id_solicitud,
            id_usuario=s.id_usuario,
            id_plomero=s.id_plomero,
            descripcion_raw=s.descripcion_raw,
            imagen_path=s.imagen_path,
            video_path=s.video_path,
            etiqueta_ia=s.etiqueta_ia,
            urgencia_ia=s.urgencia_ia,
            presupuesto_min=s.presupuesto_min,
            presupuesto_max=s.presupuesto_max,
            estado=s.estado.value if hasattr(s.estado, "value") else str(s.estado),
            fecha=s.fecha,
        )

    class Config:
        from_attributes = True