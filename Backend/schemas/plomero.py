from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

from models.plomero import EspecialidadEnum


# ─────────────────────────────
# BASE
# ─────────────────────────────
class PlomeroBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    genero: str
    localidad: str


# ─────────────────────────────
# REQUEST (REGISTER)
# ─────────────────────────────
class PlomeroRequest(PlomeroBase):
    especialidad: EspecialidadEnum
    especialidades: List[EspecialidadEnum] = Field(default_factory=list)

    otra_especialidad: Optional[str] = None

    atiende_urgencias: bool
    matricula_gas: bool

    password: str
    agenda: Optional[dict] = None


# ─────────────────────────────
# RESPONSE
# ─────────────────────────────
class PlomeroResponse(BaseModel):
    id_plomero: int

    nombre: str
    apellido: str
    email: EmailStr
    telefono: str

    especialidad: EspecialidadEnum
    especialidades: List[EspecialidadEnum] = Field(default_factory=list)

    otra_especialidad: Optional[str] = None

    genero: str
    localidad: str

    latitud: Optional[float] = None
    longitud: Optional[float] = None

    puntuacion: float
    total_trabajos: int

    atiende_urgencias: bool
    disponible_ahora: bool
    matricula_gas: bool

    foto_perfil_path: Optional[str] = None
    agenda: Optional[dict] = None

    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)