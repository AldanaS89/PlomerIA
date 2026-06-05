# models/solicitud.py
import enum

from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.orm import relationship
from database import Base


class EstadoSolicitud(enum.Enum):
    # inicial — esperando que un plomero acepte
    PENDIENTE              = "pendiente"

    # en ejecución — plomero asignado
    EN_PROGRESO            = "en_progreso"
    EN_CAMINO              = "en_camino"

    # final exitoso — ambos pueden calificar dentro de 72hs
    PENDIENTE_CALIFICACION = "pendiente_calificacion"
    COMPLETADA             = "completada"

    # final definitivo
    CANCELADA              = "cancelada"

    # flujo interno — todos rechazaron o el plomero canceló,
    # el cliente puede reintentar (máx 3 veces)
    REASIGNACION_PENDIENTE = "reasignacion_pendiente"
    SIN_RESPUESTA          = "sin_respuesta"


class Solicitud(Base):
    __tablename__ = "solicitudes"

    __table_args__ = (
        Index("ix_solicitud_usuario", "id_usuario"),
        Index("ix_solicitud_estado",  "estado"),
        Index("ix_solicitud_localidad", "localidad_evento"),
    )

    id_solicitud = Column(Integer, primary_key=True, index=True)

    id_usuario = Column(
        Integer, ForeignKey("usuarios.id_usuario"), nullable=False
    )

    # NULL hasta que el primer plomero acepta
    id_plomero = Column(
        Integer, ForeignKey("plomeros.id_plomero"), nullable=True
    )

    descripcion_raw = Column(String, nullable=False)
    imagen_path     = Column(String, nullable=True)
    video_path      = Column(String, nullable=True)

    etiqueta_ia     = Column(String, nullable=True)
    urgencia_ia     = Column(String, nullable=True)
    presupuesto_min = Column(Float,  nullable=True)
    presupuesto_max = Column(Float,  nullable=True)

    localidad_evento = Column(String, nullable=False)
    latitud_evento   = Column(Float,  nullable=True)
    longitud_evento  = Column(Float,  nullable=True)

    turno_solicitado = Column(String,   nullable=True)
    fecha_trabajo    = Column(DateTime, nullable=True)

    fecha_ultimo_envio    = Column(DateTime, nullable=True)
    intentos_reasignacion = Column(Integer,  default=0)

    # Plazo para calificar — se setea cuando el plomero marca TERMINADO
    # Vence a las 72hs. Si el actor no calificó antes, el sistema
    # registra 5 estrellas automáticas y cierra la solicitud.
    fecha_vencimiento_calificacion = Column(DateTime, nullable=True)

    estado = Column(
        SQLEnum(EstadoSolicitud, name="estado_solicitud"),
        default=EstadoSolicitud.PENDIENTE,
    )

    fecha = Column(DateTime, default=func.now())

    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    plomero = relationship("Plomero", foreign_keys=[id_plomero])
    plomeros = relationship(
        "SolicitudPlomero",
        back_populates="solicitud",
        cascade="all, delete-orphan",
    )