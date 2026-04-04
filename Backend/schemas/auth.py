from pydantic import BaseModel, EmailStr
# ── Schemas (qué datos esperamos recibir) ──────────────────
#Define que JSON esperamos recibir - FastAPI valida solo

#Lo que envia el cliente para registrarse
class RegistroRequest(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    direccion: str
    telefono: str
    latitud: float
    longitud: float
# Lo que manda el cliente para hacer login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Lo que devuelve el servidor después del login
class LoginResponse(BaseModel):
    access_token: str
    token_type:   str
    id_usuario:   int
    nombre:       str