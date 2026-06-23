from typing import Optional

from pydantic import BaseModel, EmailStr


class RegistroRequest(BaseModel):
    nombre:    str
    apellido:  str
    email:     EmailStr
    password:  str
    direccion: str
    localidad: str
    # Coordenadas elegidas en el mapa (DireccionConMapa). Si vienen, se usan
    # directamente; geocodificar queda solo como respaldo. Evita que Nominatim
    # falle del lado del servidor y caiga al centroide genérico.
    latitud:   Optional[float] = None
    longitud:  Optional[float] = None
    # telefono eliminado — reemplazado por mensajería interna