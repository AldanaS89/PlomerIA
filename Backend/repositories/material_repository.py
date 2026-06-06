# repositories/material_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.material import MaterialItem


def crear(db: Session, item: MaterialItem) -> MaterialItem:
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def listar_por_solicitud(db: Session, id_solicitud: int):
    return (
        db.query(MaterialItem)
        .filter(MaterialItem.id_solicitud == id_solicitud)
        .order_by(MaterialItem.id_item.asc())
        .all()
    )


def obtener(db: Session, id_item: int):
    return db.query(MaterialItem).filter(MaterialItem.id_item == id_item).first()


def eliminar(db: Session, item: MaterialItem):
    db.delete(item)
    db.commit()


def total_por_solicitud(db: Session, id_solicitud: int) -> float:
    total = (
        db.query(func.coalesce(func.sum(MaterialItem.cantidad * MaterialItem.precio), 0.0))
        .filter(MaterialItem.id_solicitud == id_solicitud)
        .scalar()
    )
    return float(total or 0.0)
