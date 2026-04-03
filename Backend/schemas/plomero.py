from pydantic import BaseModel, EmailStr
from typing import Optional

class PlomeroRequest(BaseModel):
    nombre:            str
    apellido:          str
    email:             EmailStr
    telefono:          str
    especialidad:      str       # PLOMERIA_GENERAL / DESTAPES / GAS_MATRICULADO / OBRA
    genero:            str       # M / F
    localidad:         str
    atiende_urgencias: bool = False
    matricula_gas:     bool = False
    password:          str

class PlomeroResponse(BaseModel):
    id_plomero:        int
    nombre:            str
    apellido:          str
    email:             str
    especialidad:      str
    genero:            str
    localidad:         str
    atiende_urgencias: bool
    disponible_ahora:  bool
    puntuacion:        float
    total_trabajos:    int

    class Config:
        from_attributes = True