from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db

from core.auth import get_plomero_actual

from schemas.disponibilidad import (
    BloqueOut,
    BloquearRequest
)

from services import disponibilidad_service


router = APIRouter(
    tags=["Disponibilidad"]
)


@router.get(
    "/{id_plomero}",
    response_model=list[BloqueOut]
)
def ver_disponibilidad(
    id_plomero: int,
    db: Session = Depends(get_db)
):

    return disponibilidad_service.ver_disponibilidad(
        db,
        id_plomero
    )


@router.post(
    "/{id_plomero}/bloquear",
    response_model=BloqueOut
)
def bloquear_horario(
    id_plomero: int,
    datos: BloquearRequest,
    db: Session = Depends(get_db),
    id_plomero_auth: int = Depends(get_plomero_actual),
):

    return disponibilidad_service.bloquear_horario(
        db,
        id_plomero,
        id_plomero_auth,
        datos
    )


@router.delete(
    "/{id_plomero}/{id_bloque}"
)
def liberar_horario(
    id_plomero: int,
    id_bloque: int,
    db: Session = Depends(get_db),
    id_plomero_auth: int = Depends(get_plomero_actual),
):

    return disponibilidad_service.liberar_horario(
        db,
        id_plomero,
        id_bloque,
        id_plomero_auth
    )