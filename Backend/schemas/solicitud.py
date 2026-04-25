# schemas/solicitud.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SolicitudCreate(BaseModel):
<<<<<<< Updated upstream
    id_plomero      : Optional[int] = None
=======
    # id_plomero ahora es opcional al inicio porque la IA sugiere, el cliente elige
    id_plomero      : Optional[int] = None 
>>>>>>> Stashed changes
    descripcion_raw : str
    localidad_evento: str # ← Agregado para el filtro de cercanía
    imagen_path     : Optional[str] = None
    video_path      : Optional[str] = None

class SolicitudResponse(BaseModel):
    id_solicitud    : int
    id_usuario      : int
    id_plomero      : Optional[int]
    
    # --- CAMPO CLAVE  ---
    # Este campo lo llenaremos en el repository haciendo un JOIN
    nombre_plomero  : Optional[str] = None # ← Para que no diga "#1"
    
    descripcion_raw : str
    imagen_path     : Optional[str]
    video_path      : Optional[str]
    
    # --- DATOS PARA IA Y GEOPY ---
    etiqueta_ia     : Optional[str]
    urgencia_ia     : Optional[str]
    ids_plomeros_sugeridos: Optional[str] = None # ← Los 5 candidatos
    localidad_evento: Optional[str] = None
    latitud_evento  : Optional[float] = None
    longitud_evento : Optional[float] = None
    
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