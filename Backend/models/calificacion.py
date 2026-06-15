# models/calificacion.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from database import Base


class Calificacion(Base):
    """
    Registra evaluaciones entre actores dentro de PlomerIA.

    autor_rol indica quién emite la calificación:
      "cliente"         → el cliente califica al plomero (trabajo terminado)
      "plomero"         → el plomero califica al cliente (trabajo terminado)
      "sistema_cliente" → penalización automática por cancelación del cliente
      "sistema_plomero" → penalización automática por cancelación del plomero
      "sistema_vencimiento" → 5 estrellas automáticas por vencimiento de plazo

    La lógica es polimórfica: las reglas de cálculo de promedio son
    idénticas para cliente y plomero, solo cambia a quién se evalúa.
    """
    __tablename__ = "calificaciones"

    id_calificacion = Column(Integer, primary_key=True, index=True)
    id_solicitud    = Column(Integer, ForeignKey("solicitudes.id_solicitud"))
    id_cliente      = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_plomero      = Column(Integer, ForeignKey("plomeros.id_plomero"))

    autor_rol       = Column(String, nullable=False, default="cliente")
    estrellas       = Column(Float,  nullable=False)
    comentario      = Column(String, nullable=True)
    fecha_resenia   = Column(DateTime, default=datetime.now)