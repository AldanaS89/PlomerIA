# models/plomero.py
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, Enum as SAEnum
from database import Base
from models.personaMixin import PersonaMixin
import enum

class EspecialidadEnum(str, enum.Enum):
    PLOMERIA_GENERAL = "PLOMERIA_GENERAL"
    DESTAPES         = "DESTAPES"
    GAS_MATRICULADO  = "GAS_MATRICULADO"
    OBRA             = "OBRA"
    OTRA             = "OTRA"

class Plomero(PersonaMixin, Base):
    __tablename__ = "plomeros"

    id_plomero        = Column(Integer, primary_key=True, index=True)
    especialidad      = Column(SAEnum(EspecialidadEnum))  # principal
    especialidades    = Column(JSON)  # extras opcionales
    otra_especialidad = Column(String, nullable=True) # solo si eligió OTRA
    genero            = Column(String)
    atiende_urgencias = Column(Boolean, default=False)
    disponible_ahora  = Column(Boolean, default=True)
    puntuacion        = Column(Float,   default=0.0)
    total_trabajos    = Column(Integer, default=0)
    matricula_gas     = Column(Boolean, default=False)
    foto_perfil_path  = Column(String, nullable=True)
    agenda            = Column(JSON,    nullable=True)
    rol               = Column(String,  default="plomero")