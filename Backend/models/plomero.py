# models/plomero.py
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, Enum as SAEnum
from database import Base
from models.personaMixin import PersonaMixin, PersonaBase
import enum


class EspecialidadEnum(str, enum.Enum):
    PLOMERIA_GENERAL = "PLOMERIA_GENERAL"
    DESTAPES         = "DESTAPES"
    GAS_MATRICULADO  = "GAS_MATRICULADO"
    OBRA             = "OBRA"
    FILTRACIONES     = "FILTRACIONES"
    CALEFACCION      = "CALEFACCION"
    OTRA             = "OTRA"


class Plomero(PersonaMixin, Base):
    __tablename__ = "plomeros"

    id_plomero                 = Column(Integer, primary_key=True, index=True)
    especialidad               = Column(SAEnum(EspecialidadEnum))
    especialidades             = Column(JSON)
    otra_especialidad          = Column(String, nullable=True)
    genero                     = Column(String)
    atiende_urgencias          = Column(Boolean, default=False)
    disponible_ahora           = Column(Boolean, default=True)
    puntuacion                 = Column(Float,   default=5.0)
    total_trabajos             = Column(Integer, default=0)
    matricula_gas              = Column(Boolean, default=False)
    foto_perfil_path           = Column(String,  nullable=True)
    agenda                     = Column(JSON,    nullable=True)
    rol                        = Column(String,  default="plomero")
    cancelaciones_consecutivas = Column(Integer, default=0)
    suspendido                 = Column(Boolean, default=False)

    def get_id(self) -> int:
        return self.id_plomero

    def get_email(self) -> str:
        return self.email

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


PersonaBase.register(Plomero)