# routers/solicitudes.py
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from services import solicitud_service
from core.auth import get_plomero_actual, get_usuario_actual, get_actor_actual
from schemas.solicitud import SolicitudCreate

router = APIRouter(tags=["Solicitudes"])


class ReprogramarBody(BaseModel):
    fecha_trabajo: datetime


class ReintentarBody(BaseModel):
    ids_plomeros_seleccionados: list[int] = []
    turnos_por_plomero: dict[str, str] = {}


class BorradorBody(BaseModel):
    descripcion: str


class ConfirmarBody(BaseModel):
    ids_plomeros_seleccionados: list[int] = []
    turnos_por_plomero: dict[str, str] = {}


# ── CREAR ─────────────────────────────────────────────────────────────────────
@router.post("/")
async def crear_solicitud(
    data: SolicitudCreate,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.crear_solicitud(db, data, id_usuario)


# ── CLIENTE ───────────────────────────────────────────────────────────────────
@router.get("/mis-solicitudes")
def mis_solicitudes(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.listar_por_usuario(db, id_usuario)


@router.get("/buscar")
def buscar(
    q: Optional[str] = "",
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.buscar_por_texto(db, q)


@router.patch("/{id_solicitud}/cancelar")
def cancelar_solicitud(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.cancelar(db, id_solicitud, id_usuario)

@router.post("/borrador")
def crear_borrador(
    body: BorradorBody,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.crear_o_actualizar_borrador(db, body.descripcion, id_usuario)


@router.post("/{id_solicitud}/confirmar")
def confirmar(
    id_solicitud: int,
    body: ConfirmarBody,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.confirmar_borrador(
        db,
        id_solicitud,
        id_usuario,
        body.ids_plomeros_seleccionados,
        body.turnos_por_plomero,
    )


@router.post("/{id_solicitud}/reintentar")
def reintentar(
    id_solicitud: int,
    body: ReintentarBody,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.reintentar(
        db,
        id_solicitud,
        id_usuario,
        body.ids_plomeros_seleccionados,
        body.turnos_por_plomero,
    )


@router.patch("/{id_solicitud}/aceptar")
def aceptar(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.aceptar(db, id_solicitud, id_plomero)

@router.patch("/{id_solicitud}/rechazar")
def rechazar(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.rechazar(db, id_solicitud, id_plomero)


@router.patch("/{id_solicitud}/en_camino")
def en_camino(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.marcar_en_camino(db, id_solicitud, id_plomero)


@router.patch("/{id_solicitud}/completar")
def completar(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.completar(db, id_solicitud, id_plomero)


@router.patch("/{id_solicitud}/reprogramar")
def reprogramar(
    id_solicitud: int,
    body: ReprogramarBody,
    db: Session = Depends(get_db),
    actor: dict = Depends(get_actor_actual),
):
    return solicitud_service.reprogramar(db, id_solicitud, actor, body.fecha_trabajo)


@router.patch("/{id_solicitud}/cancelar_plomero")
def cancelar_plomero(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return solicitud_service.cancelar_plomero(db, id_solicitud, id_plomero)


# ── PLOMERO ───────────────────────────────────────────────────────────────────
@router.get("/plomero/me")
def mis_solicitudes_plomero(
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    print("PLOMERO LOGUEADO:", id_plomero)

    return solicitud_service.listar_por_plomero(
        db,
        id_plomero
    )




# ── DINÁMICA AL FINAL ─────────────────────────────────────────────────────────
@router.get("/{id_solicitud}")
def obtener(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return solicitud_service.obtener_para_usuario(db, id_solicitud, id_usuario)