from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from Backend.database import Base

class Asignacion(Base):
    __tablename__ = "asignaciones"

    id_asignacion = Column(Integer, primary_key=True, index=True)
    id_solicitud = Column(Integer)
    id_plomero = Column(Integer)
    estado = Column(String, default="pendiente")
    fecha_aceptacion = Column(DateTime, nullable=True)
    fecha_completado = Column(DateTime, nullable=True)
