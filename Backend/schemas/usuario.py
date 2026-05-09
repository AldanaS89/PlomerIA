from pydantic import BaseModel

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre:     str
    apellido:   str
    email:      str
    telefono:   str
    localidad:  str

    class Config:
        from_attributes = True