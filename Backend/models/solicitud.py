# models/solicitud.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

# ── Estados posibles de una solicitud ────────────────────────────────────────
class EstadoSolicitud(enum.Enum):
    PENDIENTE  = "pendiente"
    ACEPTADO   = "aceptado"
    RECHAZADO  = "rechazado"

# ── Modelo principal ──────────────────────────────────────────────────────────
class Solicitud(Base):
    __tablename__ = "solicitudes"

    id_solicitud    = Column(Integer, primary_key=True, index=True)

    # ── Quién pide y a quién se le asigna ────────────────────────────────────
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_plomero      = Column(Integer, ForeignKey("plomeros.id_plomero"), nullable=True)
    #                                             ↑ nullable=True porque al crear
    #                                               la solicitud aún no hay plomero asignado

    # ── Descripción del problema (cargado por el cliente) ────────────────────
    descripcion_raw = Column(String, nullable=False)
    imagen_path     = Column(String, nullable=True)   # ruta de la foto adjunta
    video_path      = Column(String, nullable=True)   # ruta del video adjunto

    # ── Resultado del diagnóstico de la IA ───────────────────────────────────
    etiqueta_ia     = Column(String, nullable=True)   # ej: "DESTAPES"
    urgencia_ia     = Column(String, nullable=True)   # ej: "URGENTE"
    presupuesto_min = Column(Float,  nullable=True)   # en ARS
    presupuesto_max = Column(Float,  nullable=True)   # en ARS

    # ── Estado y fecha ────────────────────────────────────────────────────────
    estado          = Column(Enum(EstadoSolicitud), default=EstadoSolicitud.PENDIENTE)
    fecha           = Column(DateTime, default=datetime.now)

    # ── Relaciones (para acceder a los objetos relacionados fácilmente) ───────
    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    plomero = relationship("Plomero", foreign_keys=[id_plomero])