# schemas/solicitud.py
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List, Dict


class SolicitudCreate(BaseModel):
    descripcion_raw:              str
    localidad_evento:             str
    latitud_evento:               Optional[float] = None
    longitud_evento:              Optional[float] = None
    solo_mujeres:                 bool            = False
    ids_plomeros_seleccionados:   List[int]       = []
    turnos_por_plomero:           Dict[str, str]  = {}  # {id_plomero: "Lun_manana_9"}


class SolicitudResponse(BaseModel):
    id_solicitud:                  int
    id_usuario:                    int
    id_plomero:                    Optional[int]   = None
    nombre_plomero:                Optional[str]   = None
    descripcion_raw:               str
    ids_plomeros_sugeridos:        Optional[str]   = None
    presupuesto_min:               Optional[float] = 0.0
    presupuesto_max:               Optional[float] = 0.0
    estado:                        str
    fecha:                         datetime
    localidad_evento:              Optional[str]   = None
    latitud_evento:                Optional[float] = None
    longitud_evento:               Optional[float] = None
    etiqueta_ia:                   Optional[str]   = None
    urgencia_ia:                   Optional[str]   = None
    turno_solicitado:              Optional[str]   = None
    plomeros_sugeridos_detallados: Optional[List[dict]] = []

    @field_validator("estado", mode="before")
    @classmethod
    def serializar_estado(cls, v):
        if hasattr(v, "value"):
            return v.value
        return str(v)

    class Config:
        from_attributes = True