# repositories/notificacion_repository.py
from sqlalchemy.orm import Session
from models.notificacion import Notificacion


def crear(db: Session, notificacion: Notificacion) -> Notificacion:
    db.add(notificacion)
    db.commit()
    db.refresh(notificacion)
    return notificacion


def listar_por_destinatario(db: Session, destinatario_id: int, destinatario_rol: str):
    return (
        db.query(Notificacion)
        .filter(
            Notificacion.destinatario_id == destinatario_id,
            Notificacion.destinatario_rol == destinatario_rol,
        )
        .order_by(Notificacion.fecha.desc())
        .all()
    )


def contar_no_leidas(db: Session, destinatario_id: int, destinatario_rol: str) -> int:
    return (
        db.query(Notificacion)
        .filter(
            Notificacion.destinatario_id == destinatario_id,
            Notificacion.destinatario_rol == destinatario_rol,
            Notificacion.leida == False,  # noqa: E712
        )
        .count()
    )


def obtener_por_id(db: Session, id_notificacion: int):
    return (
        db.query(Notificacion)
        .filter(Notificacion.id_notificacion == id_notificacion)
        .first()
    )


def marcar_leida(db: Session, notificacion: Notificacion):
    notificacion.leida = True
    db.commit()
    db.refresh(notificacion)
    return notificacion


def eliminar_todas(db: Session, destinatario_id: int, destinatario_rol: str) -> int:
    """Borra todas las notificaciones del destinatario."""
    borradas = (
        db.query(Notificacion)
        .filter(
            Notificacion.destinatario_id == destinatario_id,
            Notificacion.destinatario_rol == destinatario_rol,
        )
        .delete()
    )
    db.commit()
    return borradas


def eliminar_antiguas(db: Session, antes_de) -> int:
    """Borra notificaciones con fecha anterior a `antes_de` (limpieza automática)."""
    borradas = (
        db.query(Notificacion)
        .filter(Notificacion.fecha < antes_de)
        .delete()
    )
    db.commit()
    return borradas


def marcar_todas_leidas(db: Session, destinatario_id: int, destinatario_rol: str) -> int:
    actualizadas = (
        db.query(Notificacion)
        .filter(
            Notificacion.destinatario_id == destinatario_id,
            Notificacion.destinatario_rol == destinatario_rol,
            Notificacion.leida == False,  # noqa: E712
        )
        .update({Notificacion.leida: True})
    )
    db.commit()
    return actualizadas
