# schemas/plomero.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


class PlomeroRequest(BaseModel):
    nombre:              str
    apellido:            str
    email:               EmailStr
    telefono:            str
    especialidades:      List[str]        # ["PLOMERIA_GENERAL", "DESTAPES", ...]
    otra_especialidades: Optional[str] = None
    genero:              str
    localidad:           str
    atiende_urgencias:   bool
    matricula_gas:       bool
    password:            str
    agenda:              Optional[dict] = None  # {"Lun_manana": True, ...}
    # latitud y longitud las calcula geopy — no vienen del frontend


class PlomeroResponse(BaseModel):
    id_plomero:          int
    nombre:              str
    apellido:            str
    email:               str
    telefono:            str
    especialidades:      Optional[List[str]] = []
    otra_especialidades: Optional[str] = None
    genero:              str
    localidad:           str
    latitud:             Optional[float] = None
    longitud:            Optional[float] = None
    puntuacion:          float
    total_trabajos:      int
    atiende_urgencias:   bool
    disponible_ahora:    bool
    matricula_gas:       bool
    foto_perfil_path:    Optional[str] = None
    fecha_registro:      datetime

    model_config = ConfigDict(from_attributes=True)


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
    token:          str
    nueva_password: str