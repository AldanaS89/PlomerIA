from sqlalchemy.orm import Session
from models.plomero import Plomero

def buscar_por_email(db: Session, email: str) -> Plomero | None:
    return db.query(Plomero).filter(Plomero.email == email).first()

def buscar_por_id(db: Session, id: int) -> Plomero | None:
    return db.query(Plomero).filter(Plomero.id_plomero == id).first()

def crear_plomero(db: Session, plomero: Plomero) -> Plomero:
    db.add(plomero)
    db.commit()
    db.refresh(plomero)
    return plomero

def listar_todos(db: Session) -> list[Plomero]:
    return db.query(Plomero).all()

def actualizar_disponibilidad(db: Session, id: int, disponible: bool) -> Plomero | None:
    plomero = buscar_por_id(db, id)
    if not plomero:
        return None
    plomero.disponible_ahora = disponible
    db.commit()
    db.refresh(plomero)
    return plomero

def actualizar_puntuacion(db: Session, id: int, nueva_puntuacion: float, total: int) -> None:
    plomero = buscar_por_id(db, id)
    if plomero:
        plomero.puntuacion     = nueva_puntuacion
        plomero.total_trabajos = total
        db.commit()