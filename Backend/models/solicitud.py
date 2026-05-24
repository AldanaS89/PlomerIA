# models/solicitud.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

# ── ESTADOS POSIBLES ─────────────────────────────────────────────────────────
# Esto define las fases de la solicitud para el flujo de "quien acepta primero gana"
class EstadoSolicitud(enum.Enum):
    PENDIENTE = "pendiente"        # creada, sin asignar
    ASIGNADA = "asignada"          # ya tiene plomero
    EN_PROGRESO = "en_progreso"    # plomero aceptó y está trabajando
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

class Solicitud(Base):
    __tablename__ = "solicitudes"

    id_solicitud    = Column(Integer, primary_key=True, index=True)

    # ── RELACIONES ────────────────────────────────────────────────────────────
    id_usuario      = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_plomero      = Column(Integer, ForeignKey("plomeros.id_plomero"), nullable=True) # Se llena cuando alguien acepta

    # ── DATOS DEL PROBLEMA ───────────────────────────────────────────────────
    descripcion_raw = Column(String, nullable=False)
    imagen_path     = Column(String, nullable=True)
    video_path      = Column(String, nullable=True)

    # ── DIAGNÓSTICO IA ───────────────────────────────────────────────────────
    etiqueta_ia     = Column(String, nullable=True)   # Clasificación (ej: "Gasista")
    urgencia_ia     = Column(String, nullable=True)   # Nivel de prioridad
    presupuesto_min = Column(Float,  nullable=True)
    presupuesto_max = Column(Float,  nullable=True)

    # ── NUEVOS CAMPOS PARA EL FLUJO ──────────────────────────────────────────
    # Guardamos los IDs de los 5 mejores candidatos para que el sistema sepa a quién notificar
    ids_plomeros_sugeridos = Column(String, nullable=True) # Ejemplo: "12, 45, 7, 23, 9"
    
    # Ubicación del evento (Fundamental para Geopy y cercanía)
    localidad_evento = Column(String, nullable=False) 
    latitud_evento   = Column(Float,  nullable=True) # Coordenada Y
    longitud_evento  = Column(Float,  nullable=True) # Coordenada X

    # ── ESTADO Y FECHA ───────────────────────────────────────────────────────
    estado          = Column(Enum(EstadoSolicitud), default=EstadoSolicitud.PENDIENTE)
    fecha           = Column(DateTime, default=datetime.now)

    # ── RELACIONES ORM ────────────────────────────────────────────────────────
    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    plomero = relationship("Plomero", foreign_keys=[id_plomero])