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


def hubo_intercambio(db, id_solicitud: int) -> bool:
    """True si en el chat escribieron AMBOS (cliente y plomero) — intercambio real."""
    roles = (
        db.query(Mensaje.emisor_rol)
        .filter(Mensaje.id_solicitud == id_solicitud)
        .distinct()
        .all()
    )
    roles_set = {r[0] for r in roles}
    return "usuario" in roles_set and "plomero" in roles_set