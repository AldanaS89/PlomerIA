from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

# --- SCHEMA PARA EL REGISTRO (Lo que entra desde el Swagger/App) ---
class PlomeroRequest(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    especialidad: str
    
    # Campos nuevos para las mejoras de Aldana:
    genero: str            # Para el switch de "Plomeras" en la App
    localidad: str         # Para filtrar por zonas de Almirante Brown
    latitud: float         # Coordenada para el mapa (Geopy)
    longitud: float        # Coordenada para el mapa (Geopy)
    
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
    especialidad: str
    genero: str
    localidad: str
    
    # La ubicación es opcional en la respuesta por si algún perfil no la tiene
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    
    puntuacion: float
    total_trabajos: int
    atiende_urgencias: bool
    disponible_ahora: bool
    fecha_registro: datetime

    # Permite que FastAPI convierta objetos de SQLAlchemy a este formato JSON
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

# --- SCHEMAS PARA RECUPERACIÓN DE CONTRASEÑA ---
class OlvidePasswordPlomeroRequest(BaseModel):
    email: EmailStr

class ResetPasswordPlomeroRequest(BaseModel):
    token: str
    nueva_password: str