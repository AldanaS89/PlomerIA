from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido = Column(String)
    direccion = Column(String)
    telefono = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    latitud = Column(Float)
    longitud = Column(Float)
    fecha_registro = Column(DateTime, default=datetime.now)  
    reset_token = Column(String, nullable=True)