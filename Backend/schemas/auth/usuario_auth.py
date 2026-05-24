from pydantic import BaseModel, EmailStr

# ─────────────────────────────
# REGISTRO
# ─────────────────────────────
class RegistroRequest(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    direccion: str
    localidad: str
    telefono: str | None = None


