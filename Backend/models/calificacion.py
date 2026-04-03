from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from Backend.database import Base

class Calificacion(Base):
    __tablename__ = "calificaciones"

    id_calificacion = Column(Integer, primary_key=True, index=True)
    id_asignacion = Column(Integer)
    id_cliente = Column(Integer)
    id_plomero = Column(Integer)
    estrellas = Column(Integer)
    comentario = Column(String, nullable=True)
    fecha_resenia = Column(DateTime, default=datetime.now)
