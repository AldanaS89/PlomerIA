# models/calificacion.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id_calificacion = Column(Integer, primary_key=True, index=True)
    id_solicitud    = Column(Integer, ForeignKey("solicitudes.id_solicitud"))
    id_cliente      = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_plomero      = Column(Integer, ForeignKey("plomeros.id_plomero"))
    estrellas       = Column(Integer)
    comentario      = Column(String, nullable=True)
    fecha_resenia   = Column(DateTime, default=datetime.now)