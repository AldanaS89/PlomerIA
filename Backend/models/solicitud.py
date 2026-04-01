from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SolicitudDiagnostico(BaseModel):
    id_solicitud: str
    id_usuario: str
    fecha: datetime = datetime.now()
    
    # Datos generados por la IA de Gemini
    diagnostico_ia: str  # Ejemplo: "Rotura de caño termofusión en pared"
    nivel_urgencia: str   # "Baja", "Media", "Alta/Emergencia"
    presupuesto_estimado_min: float
    presupuesto_estimado_max: float
    
    # Datos para el plomero
    fotos_adjuntas: list[str] = []
    estado: str = "Pendiente"  # Pendiente, Aceptada, Finalizada