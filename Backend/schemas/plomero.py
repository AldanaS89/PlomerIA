from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

# ── Enums ──────────────────────────────────────────────────
class Especialidad(str, Enum):
    PLOMERIA_GENERAL = "PLOMERIA_GENERAL"
    DESTAPES         = "DESTAPES"
    GAS_MATRICULADO  = "GAS_MATRICULADO"
    OBRA             = "OBRA"
    OTRA             = "OTRA"

class Genero(str, Enum):
    M = "M"
    F = "F"

class PlomeroRequest(BaseModel):
    nombre:              str
    apellido:            str
    email:               EmailStr
    telefono:            str
    especialidad:        Especialidad
    otra_especialidad:   Optional[str] = None  # solo si especialidad == OTRA
    genero:              Genero
    localidad:           str
    atiende_urgencias:   bool = False
    matricula_gas:       bool = False
    password:            str

class PlomeroResponse(BaseModel):
    id_plomero:          int
    nombre:              str
    apellido:            str
    email:               str
    especialidad:        str
    otra_especialidad:   Optional[str] = None
    genero:              str
    localidad:           str
    atiende_urgencias:   bool
    disponible_ahora:    bool
    puntuacion:          float
    total_trabajos:      int
# Le dice a Pydantic que puede convertir un objeto SQLAlchemy directamente a este schema. Sin eso, 
#PlomeroResponse.model_validate(plomero) no funcionaría.
    class Config:
        from_attributes = True
        
class PlomeroLoginRequest(BaseModel):
    email:    EmailStr
    password: str

class PlomeroLoginResponse(BaseModel):
    access_token: str
    token_type:   str
    id_plomero:   int
    nombre:       str
    
class OlvidePasswordPlomeroRequest(BaseModel):
    email: EmailStr

class ResetPasswordPlomeroRequest(BaseModel):
    token:           str
    nueva_password:  str