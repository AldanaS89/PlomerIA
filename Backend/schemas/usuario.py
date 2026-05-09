# schemas/usuario.py
from pydantic import BaseModel
from typing import Optional

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre:     str
    apellido:   str
    email:      str
    telefono:   str
    direccion:  str
    localidad:  str # ← Agregado
    latitud:    float
    longitud:   float

    class Config:
        from_attributes = True