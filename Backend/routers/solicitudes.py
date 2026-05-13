from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from services import solicitud_service
from repositories import solicitud_repository
from utils.auth_plomeros import get_usuario_actual, get_plomero_actual
from schemas.solicitud import SolicitudCreate
from models.solicitud import Solicitud, EstadoSolicitud

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


# ── CREAR SOLICITUD ───────────────────────────────────────────────────────────

@router.post("/")
async def crear_solicitud(
    data: SolicitudCreate,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.crear_solicitud(db, data, id_usuario)


# ── MIS SOLICITUDES CON DETALLE (cliente) ────────────────────────────────────
# Devuelve las solicitudes del usuario logueado con:
# - plomero asignado (si aceptó)
# - plomeros_notificados: lista con datos completos de cada uno

@router.get("/mis-solicitudes")
def mis_solicitudes_con_detalle(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_repository.listar_por_usuario_con_detalle(db, id_usuario)


# ── BUSCAR (compatibilidad con endpoint anterior) ─────────────────────────────

@router.get("/buscar")
def buscar(
    q: Optional[str] = "",
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_repository.listar_por_usuario_con_detalle(db, id_usuario)


# ── ENDPOINTS DEL PLOMERO ─────────────────────────────────────────────────────

@router.get("/plomero/me")
def mis_solicitudes_plomero(
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.listar_por_plomero_s(db, id_plomero)


@router.patch("/{id_solicitud}/responder")
def responder_solicitud(
    id_solicitud: int,
    accion: str,  # "aceptar" o "rechazar"
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="La solicitud ya no existe.")
    if solicitud.estado == EstadoSolicitud.ACEPTADO and accion == "aceptar":
        raise HTTPException(status_code=400, detail="Lo sentimos, otro plomero ya tomó este trabajo.")

    if accion == "aceptar":
        solicitud.estado     = EstadoSolicitud.ACEPTADO
        solicitud.id_plomero = id_plomero
        db.commit()
        return {"status": "ok", "mensaje": "Trabajo asignado correctamente"}
    elif accion == "rechazar":
        db.commit()
        return {"status": "ok", "mensaje": "Solicitud rechazada"}
    else:
        raise HTTPException(status_code=400, detail="Acción inválida. Usá 'aceptar' o 'rechazar'.")