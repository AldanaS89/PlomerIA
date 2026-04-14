from sqlalchemy.orm import Session
from models.plomero import Plomero
from typing import Optional

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

def buscar_disponible_para(
    db: Session,
    especialidad: Optional[str] = None,
    localidad: Optional[str] = None,
    atiende_urgencias: Optional[bool] = None,
) -> Plomero | None:
    query = db.query(Plomero).filter(Plomero.disponible_ahora == True)
    if especialidad:
        query = query.filter(Plomero.especialidad == especialidad)
    if localidad:
        query = query.filter(Plomero.localidad == localidad)
    if atiende_urgencias is True:
        query = query.filter(Plomero.atiende_urgencias == True)
    return query.order_by(Plomero.puntuacion.desc()).first()


def filtrar(
    db:                Session,
    localidad:         Optional[str]  = None,
    genero:            Optional[str]  = None,
    especialidad:      Optional[str]  = None,
    atiende_urgencias: Optional[bool] = None,
    solo_disponibles:  bool           = True,
) -> list[Plomero]:
    query = db.query(Plomero)

    if solo_disponibles:
        query = query.filter(Plomero.disponible_ahora == True)
    if localidad:
        query = query.filter(Plomero.localidad == localidad)
    if genero:
        query = query.filter(Plomero.genero == genero)
    if especialidad:
        query = query.filter(Plomero.especialidad == especialidad)
    if atiende_urgencias is not None:
        query = query.filter(Plomero.atiende_urgencias == atiende_urgencias)

    # Ordenar por puntuación descendente
    return query.order_by(Plomero.puntuacion.desc()).all()