from pydantic import BaseModel, ConfigDict


class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    email: str
    direccion: str
    localidad: str
    latitud: float
    longitud: float

    model_config = ConfigDict(from_attributes=True)