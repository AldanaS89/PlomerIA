# services/solicitud_service.py
from sqlalchemy.orm import Session
from schemas.solicitud import SolicitudCreate
from repositories.solicitud_repository import (  # ← importar directo, no desde el paquete
    crear,
    obtener_por_id,
    listar_por_usuario,
    listar_por_plomero,
    cambiar_estado
)

def crear_solicitud(db: Session, datos: SolicitudCreate, id_usuario: int):
    return crear(db, id_usuario, datos)

def obtener_por_id_s(db: Session, id: int):
    return obtener_por_id(db, id)

def listar_por_usuario_s(db: Session, id_usuario: int):
    return listar_por_usuario(db, id_usuario)

def listar_por_plomero_s(db: Session, id_plomero: int):
    return listar_por_plomero(db, id_plomero)

def cambiar_estado_s(db: Session, id: int, estado: str):
    return cambiar_estado(db, id, estado)