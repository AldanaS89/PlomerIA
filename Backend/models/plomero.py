from pydantic import BaseModel
from typing import Optional

class Plomero(BaseModel):
    id: int
    nombre: str
    especialidad: str  # Ejemplo: "Gasista", "Destapaciones"
    atiende_urgencias: bool  # Esto es el "Sí" o "No" (True/False)
    genero: str
    # Ubicación para que el vecino de Almirante Brown lo encuentre
    latitud: float
    longitud: float
    experiencia_anios: Optional[int] = None
    puntuacion: float = 0.0