import enum

from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    func,
)

from sqlalchemy.orm import relationship

from database import Base

from sqlalchemy import Enum as SQLEnum


class EstadoSolicitud(enum.Enum):
    # 🟡 inicial
    PENDIENTE = "pendiente"

    # 🔵 ejecución
    EN_PROGRESO = "en_progreso"
    EN_CAMINO = "en_camino"

    # 🟣 final exitoso
    PENDIENTE_CALIFICACION = "pendiente_calificacion"
    COMPLETADA = "completada"

    # 🔴 final definitivo
    CANCELADA = "cancelada"

    # 🟠 esperando nuevos plomeros
    REASIGNACION_PENDIENTE = "reasignacion_pendiente"
    SIN_RESPUESTA = "sin_respuesta"


class Solicitud(Base):
    __tablename__ = "solicitudes"
    
    __table_args__ = (
        Index("ix_solicitud_usuario", "id_usuario"),
        Index("ix_solicitud_estado", "estado"),
        Index("ix_solicitud_localidad", "localidad_evento"),
    )

    id_solicitud = Column(
        Integer,
        primary_key=True,
        index=True
    )

    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    # plomero que finalmente aceptó
    id_plomero = Column(
        Integer,
        ForeignKey("plomeros.id_plomero"),
        nullable=True
    )

    descripcion_raw = Column(
        String,
        nullable=False
    )

    imagen_path = Column(
        String,
        nullable=True
    )

    video_path = Column(
        String,
        nullable=True
    )

    etiqueta_ia = Column(
        String,
        nullable=True
    )

    urgencia_ia = Column(
        String,
        nullable=True
    )

    presupuesto_min = Column(
        Float,
        nullable=True
    )

    presupuesto_max = Column(
        Float,
        nullable=True
    )

    localidad_evento = Column(
        String,
        nullable=False
    )

    latitud_evento = Column(
        Float,
        nullable=True
    )

    longitud_evento = Column(
        Float,
        nullable=True
    )

    turno_solicitado = Column(
        String,
        nullable=True
    )

    fecha_trabajo = Column(
        DateTime,
        nullable=True
    )

    fecha_ultimo_envio = Column(
        DateTime,
        nullable=True
    )

    intentos_reasignacion = Column(
        Integer,
        default=0
    )

    estado = Column(
        SQLEnum(EstadoSolicitud, name="estado_solicitud"),
        default=EstadoSolicitud.PENDIENTE
    )

    fecha = Column(
        DateTime,
        default=func.now()
    )

    # Relaciones
    usuario = relationship(
        "Usuario",
        foreign_keys=[id_usuario]
    )

    plomero = relationship(
        "Plomero",
        foreign_keys=[id_plomero]
    )

    plomeros = relationship(
        "SolicitudPlomero",
        back_populates="solicitud",
        cascade="all, delete-orphan"
    )
    


