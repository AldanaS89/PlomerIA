# repositories/solicitud_repository.py
from sqlalchemy.orm import Session
from models.solicitud import Solicitud, EstadoSolicitud
from models.plomero import Plomero 
from schemas.solicitud import SolicitudCreate
from typing import List, Optional


def crear(db: Session, id_usuario: int, datos: SolicitudCreate, diagnostico: dict) -> Solicitud:
    solicitud = Solicitud(
        id_usuario             = id_usuario,
        id_plomero             = datos.id_plomero,
        descripcion_raw        = datos.descripcion_raw,
        localidad_evento       = datos.localidad_evento,
        imagen_path            = datos.imagen_path,
        video_path             = datos.video_path,
        estado                 = EstadoSolicitud.PENDIENTE
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


def asignar_plomero(db: Session, id_solicitud: int, id_plomero: int) -> Solicitud | None:
    solicitud = obtener_por_id(db, id_solicitud)
    if not solicitud:
        return None
    solicitud.id_plomero = id_plomero
    db.commit()
    db.refresh(solicitud)
    return solicitud


def obtener_por_id(db: Session, id: int) -> Solicitud | None:
    return db.query(Solicitud).filter(Solicitud.id_solicitud == id).first()


def listar_por_usuario(db: Session, id_usuario: int) -> list[Solicitud]:
    """Busca todas las solicitudes de un cliente específico."""
    return db.query(Solicitud).filter(Solicitud.id_usuario == id_usuario).all()

def listar_por_plomero(db: Session, id_plomero: int) -> list[Solicitud]:
    """Busca todas las solicitudes asignadas a un plomero."""
    return db.query(Solicitud).filter(Solicitud.id_plomero == id_plomero).all()

def listar_con_nombres(db: Session) -> list:
    """Trae todas las solicitudes unidas con el nombre del plomero."""
    resultados = db.query(
        Solicitud, 
        (Plomero.nombre + " " + Plomero.apellido).label("nombre_plomero")
    ).outerjoin(Plomero, Solicitud.id_plomero == Plomero.id_plomero).all()
    
    for solicitud, nombre in resultados:
        solicitud.nombre_plomero = nombre if nombre else "Sin asignar"
    
    return [r[0] for r in resultados]

def cambiar_estado(db: Session, id: int, nuevo_estado: str) -> Solicitud | None:
    solicitud = obtener_por_id(db, id)
    if not solicitud:
        return None
    solicitud.estado = nuevo_estado
    db.commit()
    db.refresh(solicitud)
    return solicitud

# solicitud_repository.py — agregar esta función
def guardar_ids_sugeridos(db: Session, id_solicitud: int, ids: list[int]) -> None:
    solicitud = obtener_por_id(db, id_solicitud)
    if solicitud:
        solicitud.ids_plomeros_sugeridos = ", ".join(str(i) for i in ids)
        db.commit()
