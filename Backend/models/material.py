# models/material.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from database import Base


class MaterialItem(Base):
    """
    Ítem de la boleta de materiales de un trabajo.
    El plomero los carga/edita mientras el trabajo está en curso;
    el cliente los ve como detalle del gasto.
    """
    __tablename__ = "materiales_boleta"

    id_item      = Column(Integer, primary_key=True, index=True)
    id_solicitud = Column(Integer, ForeignKey("solicitudes.id_solicitud"), index=True)

    descripcion = Column(String, nullable=False)
    cantidad    = Column(Float, default=1.0)
    precio      = Column(Float, default=0.0)   # precio unitario

    fecha = Column(DateTime, default=datetime.utcnow)
