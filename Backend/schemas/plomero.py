from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- SCHEMA PARA EL REGISTRO (Lo que entra desde el Swagger/App) ---
class PlomeroRequest(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str

    direccion: str          

    especialidades: List[str]

    genero: str
    localidad: str

    latitud: Optional[float] = None
    longitud: Optional[float] = None

    atiende_urgencias: bool
    matricula_gas: bool
    password: str

# --- SCHEMA PARA LA RESPUESTA (Lo que el sistema devuelve) ---
class PlomeroResponse(BaseModel):
    id_plomero: int
    nombre: str
    apellido: str
    email: str
    telefono: str

    especialidades: List[str]  # ✔ CAMBIO IMPORTANTE

    genero: str
    localidad: str

    latitud: Optional[float] = None
    longitud: Optional[float] = None

    puntuacion: float
    total_trabajos: int
    atiende_urgencias: bool
    disponible_ahora: bool
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)

# --- SCHEMAS PARA AUTENTICACIÓN ---
class PlomeroLoginRequest(BaseModel):
    email: EmailStr
    password: str

class PlomeroLoginResponse(BaseModel):
    access_token: str
    token_type: str
    id_plomero: int
    nombre: str
    rol: str = "plomero"
# --- SCHEMAS PARA RECUPERACIÓN DE CONTRASEÑA ---
class OlvidePasswordPlomeroRequest(BaseModel):
    email: EmailStr

class ResetPasswordPlomeroRequest(BaseModel):
    token: str
    nueva_password: str