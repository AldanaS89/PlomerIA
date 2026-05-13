# Backend/schemas/solicitud.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SolicitudCreate(BaseModel):
    descripcion_raw             : str
    solo_mujeres                : Optional[bool] = False
    localidad_evento            : Optional[str] = "Longchamps"
    latitud_evento              : Optional[float] = -34.85
    longitud_evento             : Optional[float] = -58.38
    ids_plomeros_seleccionados  : Optional[list] = []  # IDs elegidos por el cliente

class SolicitudResponse(BaseModel):
    id_solicitud    : int
    id_usuario      : int
    id_plomero      : Optional[int] = None
    nombre_plomero  : Optional[str] = None
    descripcion_raw : str
    ids_plomeros_sugeridos: Optional[str] = None
    presupuesto_min : Optional[float] = 0.0
    presupuesto_max : Optional[float] = 0.0
    estado          : str
    fecha           : datetime
    plomeros_sugeridos_detallados: Optional[List[dict]] = []

    class Config:
        from_attributes = True