from sqlalchemy.orm import Session
from models.mensaje import Mensaje


def crear(db, mensaje):
    db.add(mensaje)
    db.commit()
    db.refresh(mensaje)
    return mensaje


def listar_por_solicitud(db, id_solicitud: int):
    return (
        db.query(Mensaje)
        .filter(Mensaje.id_solicitud == id_solicitud)
        .order_by(Mensaje.fecha.asc())
        .all()
    )