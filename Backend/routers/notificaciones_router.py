# routers/notificaciones_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from core.auth import get_actor_actual
from schemas.notificacion import NotificacionResponse
from services import notificaciones_inapp

router = APIRouter(tags=["Notificaciones"])


@router.get("/", response_model=List[NotificacionResponse])
def listar(
    db: Session = Depends(get_db),
    actor: dict = Depends(get_actor_actual),
):
    """Lista las notificaciones del actor logueado (cliente o plomero)."""
    return notificaciones_inapp.listar(db, actor["id"], actor["role"])


@router.patch("/leer-todas")
def marcar_todas(
    db: Session = Depends(get_db),
    actor: dict = Depends(get_actor_actual),
):
    cantidad = notificaciones_inapp.marcar_todas_leidas(db, actor["id"], actor["role"])
    return {"actualizadas": cantidad}


@router.delete("/")
def borrar_todas(
    db: Session = Depends(get_db),
    actor: dict = Depends(get_actor_actual),
):
    cantidad = notificaciones_inapp.eliminar_todas(db, actor["id"], actor["role"])
    return {"borradas": cantidad}


@router.patch("/{id_notificacion}/leer")
def marcar_una(
    id_notificacion: int,
    db: Session = Depends(get_db),
    actor: dict = Depends(get_actor_actual),
):
    notif = notificaciones_inapp.marcar_leida(
        db, id_notificacion, actor["id"], actor["role"]
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return {"ok": True}
