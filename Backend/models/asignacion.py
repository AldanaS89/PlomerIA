from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from datetime import datetime
from database import Base

class Asignacion(Base):
    __tablename__ = "asignaciones"

    id_asignacion = Column(Integer, primary_key=True, index=True)
    id_solicitud = Column(Integer, ForeignKey("solicitudes.id_solicitud"))
    id_plomero   = Column(Integer, ForeignKey("plomeros.id_plomero"))
    estado = Column(String, default="pendiente")
    fecha_aceptacion = Column(DateTime, nullable=True)
    fecha_completado = Column(DateTime, nullable=True)
