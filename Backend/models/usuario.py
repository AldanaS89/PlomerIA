from sqlalchemy import Column, Integer, String
from database import Base
from models.personaMixin import PersonaMixin, PersonaBase


class Usuario(PersonaMixin, Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    direccion  = Column(String)
    rol        = Column(String, default="cliente")

    def get_id(self) -> int:
        return self.id_usuario

    def get_email(self) -> str:
        return self.email

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


# Registrar como implementación de PersonaBase sin herencia directa
# Esto evita el conflicto de metaclases entre SQLAlchemy y ABC
# pero mantiene el polimorfismo — isinstance(usuario, PersonaBase) = True
PersonaBase.register(Usuario)