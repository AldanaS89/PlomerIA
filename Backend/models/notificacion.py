# models/notificacion.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base


class Notificacion(Base):
    """
    Notificación in-app persistente para cualquiera de los dos actores.

    A diferencia del envío de mails (notificacion_service), esto vive en la
    base y alimenta la pestaña "Alertas" tanto del cliente como del plomero.
    El campo destinatario_rol permite reutilizar la misma tabla para ambos
    actores sin duplicar tablas (mismo criterio polimórfico que el resto del
    dominio: el rol define el actor).
    """
    __tablename__ = "notificaciones"

    id_notificacion = Column(Integer, primary_key=True, index=True)

    # A quién le llega
    destinatario_id  = Column(Integer, nullable=False, index=True)
    destinatario_rol = Column(String,  nullable=False)  # usuario | plomero

    # Categoría — usada por el frontend para elegir el ícono
    tipo = Column(String, nullable=False)

    titulo  = Column(String, nullable=False)
    mensaje = Column(String, nullable=False)

    # Solicitud relacionada (opcional)
    id_solicitud = Column(
        Integer, ForeignKey("solicitudes.id_solicitud"), nullable=True
    )

    leida = Column(Boolean, default=False)
    fecha = Column(DateTime, default=datetime.utcnow)
