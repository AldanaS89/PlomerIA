# models/solicitud.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class EstadoSolicitud(enum.Enum):
    PENDIENTE              = "pendiente"
    ASIGNADA               = "asignada"
    EN_PROGRESO            = "en_progreso"
    PENDIENTE_CALIFICACION = "pendiente_calificacion"  # trabajo terminado, esperando calificación
    COMPLETADA             = "completada"              # calificado — flujo cerrado
    CANCELADA              = "cancelada"


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id_solicitud    = Column(Integer, primary_key=True, index=True)

    # ── RELACIONES ────────────────────────────────────────────────────────────
    id_usuario      = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_plomero      = Column(Integer, ForeignKey("plomeros.id_plomero"), nullable=True)

    # ── DATOS DEL PROBLEMA ───────────────────────────────────────────────────
    descripcion_raw = Column(String, nullable=False)
    imagen_path     = Column(String, nullable=True)
    video_path      = Column(String, nullable=True)

    # ── DIAGNÓSTICO IA ───────────────────────────────────────────────────────
    etiqueta_ia     = Column(String, nullable=True)
    urgencia_ia     = Column(String, nullable=True)
    presupuesto_min = Column(Float,  nullable=True)
    presupuesto_max = Column(Float,  nullable=True)

    # ── PLOMEROS SUGERIDOS ───────────────────────────────────────────────────
    ids_plomeros_sugeridos = Column(String, nullable=True)

    # ── UBICACIÓN ────────────────────────────────────────────────────────────
    localidad_evento = Column(String, nullable=False)
    latitud_evento   = Column(Float,  nullable=True)
    longitud_evento  = Column(Float,  nullable=True)

    # ── ESTADO Y FECHA ───────────────────────────────────────────────────────
    estado = Column(
        Enum(EstadoSolicitud),
        default=EstadoSolicitud.PENDIENTE
    )
    fecha  = Column(DateTime, default=datetime.now)

    # ── RELACIONES ORM ────────────────────────────────────────────────────────
    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    plomero = relationship("Plomero", foreign_keys=[id_plomero])