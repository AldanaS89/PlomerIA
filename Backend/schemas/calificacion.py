# schemas/calificacion.py
from fastapi import Depends
from pydantic import BaseModel, Field
from typing import Optional




class CalificacionRequest(BaseModel):
    estrellas:  int           = Field(..., ge=1, le=5, description="1 a 5 estrellas")
    comentario: Optional[str] = None

