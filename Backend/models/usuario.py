from pydantic import BaseModel
from typing import Optional

class Usuario(BaseModel):
    nombre: str
    dni: str
    direccion: str
    # Estos dos son para que la app sepa dónde está el usuario en el mapa
    latitud: float
    longitud: float
    telefono: Optional[str] = None