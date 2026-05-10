from sqlalchemy.orm import Session
from models.plomero import Plomero
from typing import Optional, List
from math import radians, sin, cos, sqrt, atan2

RADIO_KM = 5.0

# ─────────────────────────────
# CRUD BÁSICO
# ─────────────────────────────

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


# ─────────────────────────────
# ACTUALIZACIONES
# ─────────────────────────────

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
        plomero.puntuacion = nueva_puntuacion
        plomero.total_trabajos = total
        db.commit()


# ─────────────────────────────
# RESET PASSWORD
# ─────────────────────────────

def guardar_reset_token(db: Session, id_plomero: int, token: str) -> None:
    plomero = buscar_por_id(db, id_plomero)
    if not plomero:
        return

    plomero.reset_token = token
    db.commit()


def buscar_por_reset_token(db: Session, token: str) -> Plomero | None:
    return db.query(Plomero).filter(Plomero.reset_token == token).first()


def actualizar_password(db: Session, id_plomero: int, nuevo_hash: str) -> None:
    plomero = buscar_por_id(db, id_plomero)
    if not plomero:
        return

    plomero.password_hash = nuevo_hash
    plomero.reset_token = None
    db.commit()


# ─────────────────────────────
# DISTANCIA
# ─────────────────────────────

def _distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


# ─────────────────────────────
# BÚSQUEDA PARA SOLICITUD
# ─────────────────────────────

def buscar_para_solicitud(
    db: Session,
    especialidades: Optional[str] = None,
    lat_usuario: Optional[float] = None,
    lon_usuario: Optional[float] = None,
    atiende_urgencias: bool = False,
    limite: int = 3,
) -> list[Plomero]:

    query = db.query(Plomero).filter(Plomero.disponible_ahora == True)

    if especialidades:
        # JSON array contiene especialidades
        query = query.filter(Plomero.especialidades.contains([especialidades]))

    if atiende_urgencias:
        query = query.filter(Plomero.atiende_urgencias == True)

    plomeros = query.order_by(Plomero.puntuacion.desc()).all()

    # filtro por distancia
    if lat_usuario is not None and lon_usuario is not None:
        plomeros = [
            p for p in plomeros
            if p.latitud and p.longitud and
            _distancia_km(lat_usuario, lon_usuario, p.latitud, p.longitud) <= RADIO_KM
        ]

    return plomeros[:limite]


# ─────────────────────────────
# FILTRO GENERAL
# ─────────────────────────────

def filtrar(
    db: Session,
    localidad: Optional[str] = None,
    genero: Optional[str] = None,
    especialidades: Optional[str] = None,
    atiende_urgencias: Optional[bool] = None,
    solo_disponibles: bool = True,
) -> list[Plomero]:

    query = db.query(Plomero)

    if solo_disponibles:
        query = query.filter(Plomero.disponible_ahora == True)

    if localidad:
        query = query.filter(Plomero.localidad == localidad)

    if genero:
        query = query.filter(Plomero.genero == genero)

    if especialidades:
        # JSON contains
        query = query.filter(Plomero.especialidades.contains([especialidades]))

    if atiende_urgencias is not None:
        query = query.filter(Plomero.atiende_urgencias == atiende_urgencias)

    return query.order_by(Plomero.puntuacion.desc()).all()