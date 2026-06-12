# models/usuario.py
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from database import Base
from models.personaMixin import PersonaMixin, PersonaBase


class Usuario(PersonaMixin, Base):
    __tablename__ = "usuarios"

    id_usuario                 = Column(Integer, primary_key=True, index=True)
    direccion                  = Column(String)
    rol                        = Column(String, default="cliente")
    cancelaciones_consecutivas = Column(Integer, default=0)
    suspendido                 = Column(Boolean, default=False)
    # Fecha hasta la que dura la suspensión (None = no suspendido / permanente).
    # Cuando pasa esa fecha, la cuenta se reactiva sola al volver a usarla.
    suspendido_hasta           = Column(DateTime, nullable=True)
    # Cantidad de mensajes con groserías acumulados (a las 3 → suspensión).
    mensajes_ofensivos         = Column(Integer, default=0)

    # Reputación del cliente — evaluada por los plomeros
    # Arranca en 5.0 por defecto (mismo criterio que el plomero)
    puntuacion     = Column(Float,   default=5.0)
    total_trabajos = Column(Integer, default=0)

    def get_id(self) -> int:
        return self.id_usuario

    def get_email(self) -> str:
        return self.email

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


PersonaBase.register(Usuario)