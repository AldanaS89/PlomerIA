from pydantic import BaseModel, EmailStr


class RegistroRequest(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    direccion: str
    localidad: str
    telefono: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    id_usuario: int
    nombre: str


class OlvidePasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    nueva_password: str