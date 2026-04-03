from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from Backend.database import Base

class Plomero(Base):
    __tablename__ = "plomeros"

    id_plomero = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido = Column(String)
    email = Column(String, unique=True, index=True)
    telefono = Column(String)
    especialidad = Column(String)
    genero = Column(String)
    localidad = Column(String)
    atiende_urgencias = Column(Boolean, default=False)
    disponible_ahora = Column(Boolean, default=True)
    puntuacion = Column(Float, default=0.0)
    total_trabajos = Column(Integer, default=0)
    matricula_gas = Column(Boolean, default=False)
    password_hash = Column(String)
    fecha_registro = Column(DateTime, default=datetime.now)