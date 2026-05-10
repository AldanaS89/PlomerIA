# schemas/auth.py
#Lo que envia el cliente para registrarse
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class RegistroRequest(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    direccion: str
    localidad: str
    telefono: str
    rol: Literal["cliente", "plomero"]
    # Ponelos como Optional para que el Frontend no esté obligado a enviarlos
    latitud: Optional[float] = None 
    longitud: Optional[float] = None
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Lo que devuelve el servidor después del login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    id_usuario: int
    nombre: str
    rol: str
class OlvidePasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token:        str
    nueva_password: str



