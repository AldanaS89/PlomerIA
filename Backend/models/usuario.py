from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido = Column(String)
    localidad = Column(String)
    telefono = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    fecha_registro = Column(DateTime, default=datetime.now)
