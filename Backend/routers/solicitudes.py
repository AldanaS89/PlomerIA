# routers/solicitudes.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db

from services import solicitud_service
from core.auth import get_plomero_actual, get_usuario_actual

from schemas.solicitud import SolicitudCreate


router = APIRouter(
    tags=["Solicitudes"]
)


# ─────────────────────────────
# CREAR SOLICITUD
# ─────────────────────────────

@router.post("/")
async def crear_solicitud(
    data: SolicitudCreate,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.crear_solicitud(
        db,
        data,
        id_usuario
    )


# ─────────────────────────────
# CLIENTE
# ─────────────────────────────

@router.get("/mis-solicitudes")
def mis_solicitudes(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.listar_por_usuario_con_detalle_s(
        db,
        id_usuario
    )


@router.get("/buscar")
def buscar(
    q: Optional[str] = "",
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.buscar_por_texto(
        db,
        q
    )

# ─────────────────────────────
# PLOMERO
# ─────────────────────────────

@router.get("/plomero/me")
def mis_solicitudes_plomero(
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.listar_por_plomero_s(
        db,
        id_plomero
    )
@router.patch("/{id_solicitud}/aceptar")
def aceptar(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.aceptar(
        db,
        id_solicitud,
        id_plomero
    )
    
@router.patch("/{id_solicitud}/rechazar")
def rechazar(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.rechazar(
        db,
        id_solicitud,
        id_plomero
    )   
    
@router.patch("/{id_solicitud}/completar")
def completar(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.completar(
        db,
        id_solicitud,
        id_plomero
    )
       
@router.patch("/{id_solicitud}/cancelar")
def cancelar_solicitud(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.cancelar_solicitud(
        db,
        id_solicitud,
        id_usuario
    )

# ── RUTA DINÁMICA AL FINAL ──────────────────────────────────── 
@router.get("/{id_solicitud}")
def obtener(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.obtener_para_usuario(
        db,
        id_solicitud,
        id_usuario
    )






