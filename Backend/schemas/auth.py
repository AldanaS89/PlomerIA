# schemas/auth.py
#Lo que envia el cliente para registrarse
from pydantic import BaseModel, EmailStr
from typing import Optional

class RegistroRequest(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    direccion: str
    localidad: str # ← Agregado para organizar por zonas (Almirante Brown)
    telefono: str
    latitud: float
    longitud: float# Lo que manda el cliente para hacer login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Lo que devuelve el servidor después del login
class LoginResponse(BaseModel):
    access_token: str
    token_type:   str
    id_usuario:   int
    nombre:       str
class OlvidePasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token:        str
    nueva_password: str