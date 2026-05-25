# schemas/solicitud.py
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List


class SolicitudCreate(BaseModel):
    descripcion_raw:  str
    localidad_evento: str
    latitud_evento:   float | None = None
    longitud_evento:  float | None = None


class SolicitudResponse(BaseModel):
    id_solicitud:                 int
    id_usuario:                   int
    id_plomero:                   Optional[int]   = None
    nombre_plomero:               Optional[str]   = None
    descripcion_raw:              str
    ids_plomeros_sugeridos:       Optional[str]   = None
    presupuesto_min:              Optional[float] = 0.0
    presupuesto_max:              Optional[float] = 0.0
    estado:                       str
    fecha:                        datetime
    plomeros_sugeridos_detallados: Optional[List[dict]] = []

    @field_validator("estado", mode="before")
    @classmethod
    def serializar_estado(cls, v):
        """
        Convierte el Enum de EstadoSolicitud a string
        para que el response siempre devuelva texto legible.
        Ejemplo: EstadoSolicitud.EN_PROGRESO → "en_progreso"
        """
        if hasattr(v, "value"):
            return v.value
        return str(v)

    class Config:
        from_attributes = True