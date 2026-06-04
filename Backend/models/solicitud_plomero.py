from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Enum,
    DateTime,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class EstadoInvitacion(enum.Enum):
    CONTACTADO = "contactado"
    ACEPTADO = "aceptado"
    RECHAZADO = "rechazado"
    CANCELADO = "cancelado"
    SIN_RESPUESTA = "sin_respuesta"


class SolicitudPlomero(Base):
    __tablename__ = "solicitud_plomero"

    __table_args__ = (
        UniqueConstraint(
            "id_solicitud",
            "id_plomero",
            name="uq_solicitud_plomero"
        ),
    )

    id = Column(Integer, primary_key=True)

    id_solicitud = Column(
        Integer,
        ForeignKey("solicitudes.id_solicitud"),
        nullable=False,
    )

    id_plomero = Column(
        Integer,
        ForeignKey("plomeros.id_plomero"),
        nullable=False,
    )

    estado = Column(
        Enum(EstadoInvitacion),
        nullable=False,
        default=EstadoInvitacion.CONTACTADO,
    )

    fecha = Column(DateTime, default=func.now())

    plomero = relationship("Plomero")
    solicitud = relationship(
    "Solicitud",
    back_populates="plomeros"
)