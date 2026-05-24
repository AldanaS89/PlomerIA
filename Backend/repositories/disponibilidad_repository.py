# repositories/disponibilidad_repository.py

from datetime import datetime

from sqlalchemy.orm import Session

from models.bloqueHorario import BloqueHorario


# ─────────────────────────────────────────────
# OBTENER DISPONIBLES
# ─────────────────────────────────────────────

def obtener_disponibles(
    db: Session,
    id_plomero: int,
    desde: datetime,
    hasta: datetime
):

    return (
        db.query(BloqueHorario)
        .filter(
            BloqueHorario.id_plomero == id_plomero,
            BloqueHorario.inicio >= desde,
            BloqueHorario.fin <= hasta
        )
        .order_by(BloqueHorario.inicio.asc())
        .all()
    )


# ─────────────────────────────────────────────
# CREAR BLOQUE
# ─────────────────────────────────────────────

def crear_bloque(
    db: Session,
    bloque: BloqueHorario
):

    db.add(bloque)

    db.commit()
    db.refresh(bloque)

    return bloque


# ─────────────────────────────────────────────
# BUSCAR BLOQUE
# ─────────────────────────────────────────────

def buscar_bloque(
    db: Session,
    id_bloque: int,
    id_plomero: int
):

    return (
        db.query(BloqueHorario)
        .filter(
            BloqueHorario.id == id_bloque,
            BloqueHorario.id_plomero == id_plomero
        )
        .first()
    )


# ─────────────────────────────────────────────
# ELIMINAR BLOQUE
# ─────────────────────────────────────────────

def eliminar_bloque(
    db: Session,
    bloque: BloqueHorario
):

    db.delete(bloque)

    db.commit()