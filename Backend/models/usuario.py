# models/usuario.py
from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from models.personaMixin import PersonaMixin, PersonaBase


class Usuario(PersonaMixin, Base):
    __tablename__ = "usuarios"

    id_usuario               = Column(Integer, primary_key=True, index=True)
    direccion                = Column(String)
    rol                      = Column(String, default="cliente")
    cancelaciones_consecutivas = Column(Integer, default=0)
    suspendido               = Column(Boolean, default=False)

    def get_id(self) -> int:
        return self.id_usuario

    def get_email(self) -> str:
        return self.email

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


PersonaBase.register(Usuario)