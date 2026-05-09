# models/usuario.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String)
    apellido   = Column(String)
    
    # ── PRIVACIDAD Y GEOLOCALIZACIÓN ──────────────────────────────────────────
    # La dirección completa solo se enviará al plomero que acepte el trabajo.
    # La localidad sirve para el filtrado rápido inicial (ej: "San José").
    direccion  = Column(String)
    localidad  = Column(String) # ← NUEVO: Clave para filtrar plomeros cercanos
    
    telefono   = Column(String)
    email      = Column(String, unique=True, index=True)
    password_hash = Column(String)

    # ── COORDENADAS PARA GEOPY ───────────────────────────────────────────────
    # Se calculan automáticamente al registrarse para medir distancias.
    latitud    = Column(Float)
    longitud   = Column(Float)

    fecha_registro = Column(DateTime, default=datetime.now)  
    reset_token    = Column(String, nullable=True)
