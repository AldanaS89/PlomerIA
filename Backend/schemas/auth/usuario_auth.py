from pydantic import BaseModel, EmailStr


class RegistroRequest(BaseModel):
    nombre:    str
    apellido:  str
    email:     EmailStr
    password:  str
    direccion: str
    localidad: str
    # telefono eliminado — reemplazado por mensajería interna