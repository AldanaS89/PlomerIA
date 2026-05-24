from abc import ABC, abstractmethod

from sqlalchemy.orm import declarative_mixin
from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime

@declarative_mixin
class PersonaMixin:
    nombre        = Column(String)
    apellido      = Column(String)
    email         = Column(String, unique=True, index=True)
    password_hash = Column(String)
    telefono       = Column(String)
    latitud       = Column(Float)
    longitud      = Column(Float)
    reset_token   = Column(String, nullable=True)
    fecha_registro= Column(DateTime, default=datetime.utcnow)
    localidad     = Column(String)
    
