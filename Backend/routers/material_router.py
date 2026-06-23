# routers/material_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from core.auth import get_actor_actual, get_plomero_actual
from schemas.material import MaterialCreate
from services import material_service

router = APIRouter(tags=["Boleta"])


@router.get("/{id_solicitud}")
def ver_boleta(
    id_solicitud: int,
    db: Session = Depends(get_db),
    actor: dict = Depends(get_actor_actual),
):
    # Cliente o plomero de la solicitud ven el detalle de materiales.
    return material_service.listar(db, id_solicitud, actor)


@router.post("/{id_solicitud}")
def agregar_item(
    id_solicitud: int,
    datos: MaterialCreate,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return material_service.agregar(db, id_solicitud, datos, id_plomero)


@router.delete("/item/{id_item}")
def borrar_item(
    id_item: int,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return material_service.eliminar(db, id_item, id_plomero)
