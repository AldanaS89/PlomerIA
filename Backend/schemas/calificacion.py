# schemas/calificacion.py
from pydantic import BaseModel, Field
from typing import Optional


class CalificacionRequest(BaseModel):
    """Schema para que el cliente califique al plomero. Acepta comentario opcional."""
    estrellas:  float         = Field(..., ge=1, le=5, description="1 a 5 estrellas (acepta decimales como 4.5)")
    comentario: Optional[str] = None


class CalificacionPlomeroRequest(BaseModel):
    """
    Schema para que el plomero califique al cliente.
    Solo estrellas, sin texto — mantiene la calificación simple y confiable.
    """
    estrellas: float = Field(..., ge=1, le=5, description="1 a 5 estrellas")