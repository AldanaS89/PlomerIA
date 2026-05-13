# models/plomero.py — VERSIÓN ACTUALIZADA
# Cambios:
# - especialidad (String) → especialidades (JSON list)
# - + foto_perfil_path (String)
# - + agenda (JSON dict, opcional — alternativa a tabla bloques)
from sqlalchemy import JSON, Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from database import Base


class Plomero(Base):
    __tablename__ = "plomeros"

    id_plomero          = Column(Integer, primary_key=True, index=True)
    nombre              = Column(String)
    apellido            = Column(String)
    email               = Column(String, unique=True, index=True, nullable=False)
    telefono            = Column(String)

    # Lista de especialidades: ["DESTAPES", "GAS_MATRICULADO", ...]
    especialidades      = Column(JSON)
    otra_especialidades = Column(String, nullable=True)

    genero              = Column(String)
    localidad           = Column(String)
    latitud             = Column(Float)
    longitud            = Column(Float)
    atiende_urgencias   = Column(Boolean, default=False)
    disponible_ahora    = Column(Boolean, default=True)
    puntuacion          = Column(Float, default=0.0)
    total_trabajos      = Column(Integer, default=0)
    matricula_gas       = Column(Boolean, default=False)
    password_hash       = Column(String)
    fecha_registro      = Column(DateTime, default=datetime.utcnow)
    reset_token         = Column(String, nullable=True)

    # Foto de perfil — ruta al archivo guardado en el servidor
    foto_perfil_path    = Column(String, nullable=True)

    # Agenda semanal: {"Lun_manana": true, "Lun_tarde": false, ...}
    agenda              = Column(JSON, nullable=True)