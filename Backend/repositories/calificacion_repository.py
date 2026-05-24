# repositories/calificacion_repository.py
from sqlalchemy.orm import Session
from models.calificacion import Calificacion

def crear_calificacion(db: Session, id_solicitud: int, id_plomero: int,
          id_cliente: int, estrellas: int, comentario: str | None) -> Calificacion:
    nueva = Calificacion(
        id_solicitud = id_solicitud,
        id_plomero   = id_plomero,
        id_cliente   = id_cliente,
        estrellas    = estrellas,
        comentario   = comentario,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def calcular_promedio(db: Session, id_plomero: int) -> float:
    calificaciones = db.query(Calificacion).filter(
        Calificacion.id_plomero == id_plomero
    ).all()
    if not calificaciones:
        return 0.0
    return round(sum(c.estrellas for c in calificaciones) / len(calificaciones), 1)

def ya_califico(db: Session, id_solicitud: int, id_cliente: int) -> bool:
    """Evita que el mismo cliente califique dos veces el mismo trabajo."""
    return db.query(Calificacion).filter(
        Calificacion.id_solicitud == id_solicitud,
        Calificacion.id_cliente   == id_cliente,
    ).first() is not None