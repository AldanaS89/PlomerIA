from abc import ABC, abstractmethod
from sqlalchemy.orm import declarative_mixin
from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime


@declarative_mixin
class PersonaMixin:
    nombre         = Column(String)
    apellido       = Column(String)
    email          = Column(String, unique=True, index=True)
    password_hash  = Column(String)
    # telefono eliminado — reemplazado por mensajería interna
    latitud        = Column(Float)
    longitud       = Column(Float)
    reset_token    = Column(String, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    localidad      = Column(String)


class PersonaBase(ABC):
    """
    Contrato abstracto compartido por Usuario y Plomero.
    No se hereda directamente para evitar conflicto de metaclases
    con SQLAlchemy — se usa PersonaBase.register() en cada modelo.
    Permite polimorfismo — isinstance(obj, PersonaBase) = True
    para cualquier clase registrada.
    Cumple el principio L de SOLID (Sustitución de Liskov).
    """

    @abstractmethod
    def get_id(self) -> int:
        pass

    @abstractmethod
    def get_email(self) -> str:
        pass

    @abstractmethod
    def nombre_completo(self) -> str:
        pass