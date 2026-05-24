from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base

class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True)
    id_solicitud = Column(Integer, ForeignKey("solicitudes.id_solicitud"))

    emisor_id = Column(Integer)
    emisor_rol = Column(String)  # usuario | plomero

    texto = Column(String)

    fecha = Column(DateTime, default=datetime.utcnow)
    leido = Column(Boolean, default=False)