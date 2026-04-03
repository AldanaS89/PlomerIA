from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from Backend.database import Base

class Solicitud(Base):
    __tablename__ = "solicitudes"

    id_solicitud = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer)
    descripcion_raw = Column(String)
    imagen_path = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    etiqueta_ia = Column(String, nullable=True)
    urgencia_ia = Column(String, nullable=True)
    presupuesto_min = Column(Float, nullable=True)
    presupuesto_max = Column(Float, nullable=True)
    estado = Column(String, default="pendiente")
    fecha = Column(DateTime, default=datetime.now)
