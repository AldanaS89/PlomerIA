# models/solicitud.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class EstadoSolicitud(enum.Enum):
    PENDIENTE              = "pendiente"
    ASIGNADA               = "asignada"
    EN_PROGRESO            = "en_progreso"       # plomero aceptó
    EN_CAMINO              = "en_camino"          # plomero confirmó que va
    PENDIENTE_CALIFICACION = "pendiente_calificacion"  # trabajo terminado
    COMPLETADA             = "completada"          # calificado
    CANCELADA              = "cancelada"


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id_solicitud    = Column(Integer, primary_key=True, index=True)

    id_usuario      = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_plomero      = Column(Integer, ForeignKey("plomeros.id_plomero"), nullable=True)

    descripcion_raw = Column(String, nullable=False)
    imagen_path     = Column(String, nullable=True)
    video_path      = Column(String, nullable=True)

    etiqueta_ia     = Column(String, nullable=True)
    urgencia_ia     = Column(String, nullable=True)
    presupuesto_min = Column(Float,  nullable=True)
    presupuesto_max = Column(Float,  nullable=True)

    ids_plomeros_sugeridos = Column(String, nullable=True)

    localidad_evento = Column(String, nullable=False)
    latitud_evento   = Column(Float,  nullable=True)
    longitud_evento  = Column(Float,  nullable=True)

    turno_solicitado = Column(String, nullable=True)
    fecha_trabajo = Column(DateTime, nullable=True)

    estado = Column(Enum(EstadoSolicitud), default=EstadoSolicitud.PENDIENTE)
    fecha  = Column(DateTime, default=datetime.now)

    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    plomero = relationship("Plomero", foreign_keys=[id_plomero])