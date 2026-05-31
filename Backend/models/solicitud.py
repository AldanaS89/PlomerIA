# models/solicitud.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class EstadoSolicitud(enum.Enum):
    # 🟡 inicial
    PENDIENTE = "pendiente"
    ASIGNADA = "asignada"

    # 🔵 ejecución
    EN_PROGRESO = "en_progreso"
    EN_CAMINO = "en_camino"

    # 🟣 final exitoso
    PENDIENTE_CALIFICACION = "pendiente_calificacion"
    COMPLETADA = "completada"

    # 🔴 final definitivo
    CANCELADA = "cancelada"

    # 🟠 flujo interno del sistema (CLAVE)
    REASIGNACION_PENDIENTE = "reasignacion_pendiente"


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
    ids_plomeros_contactados = Column(String, nullable=True)
    ids_plomeros_activos     = Column(String, nullable=True)

    localidad_evento = Column(String, nullable=False)
    latitud_evento   = Column(Float,  nullable=True)
    longitud_evento  = Column(Float,  nullable=True)

    turno_solicitado = Column(String, nullable=True)
    fecha_trabajo = Column(DateTime, nullable=True)
    
    fecha_ultimo_envio = Column(DateTime, nullable=True)
    intentos_reasignacion = Column(Integer, default=0)

    estado = Column(Enum(EstadoSolicitud), default=EstadoSolicitud.PENDIENTE)
    fecha  = Column(DateTime, default=datetime.now)

    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    plomero = relationship("Plomero", foreign_keys=[id_plomero])