from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base

class Mensaje(Base):
    __tablename__ = "mensajes"

    # La tabla ya existía con la columna PK llamada "id".
    # Mapeamos el atributo id_mensaje a esa columna real para no romper la
    # base existente (create_all no altera tablas ya creadas).
    id_mensaje = Column("id", Integer, primary_key=True)
    id_solicitud = Column(Integer, ForeignKey("solicitudes.id_solicitud"))

    emisor_id = Column(Integer)
    emisor_rol = Column(String)  # usuario | plomero

    texto = Column(String)

    fecha = Column(DateTime, default=datetime.utcnow)
    leido = Column(Boolean, default=False)