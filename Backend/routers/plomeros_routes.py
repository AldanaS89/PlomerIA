# routers/plomeros.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from schemas.plomero import (PlomeroRequest, PlomeroResponse,
                              PlomeroLoginRequest, PlomeroLoginResponse, OlvidePasswordPlomeroRequest, ResetPasswordPlomeroRequest)
from services import plomero_service
from utils.auth_plomeros import get_plomero_actual

router = APIRouter(prefix="/plomeros", tags=["Plomeros"])


@router.post("/registro")
def registrar(datos: PlomeroRequest, db: Session = Depends(get_db)):
    return plomero_service.registrar(db, datos)

@router.post("/login", response_model=PlomeroLoginResponse)
def login(datos: PlomeroLoginRequest, db: Session = Depends(get_db)):
    return plomero_service.login(db, datos)

@router.get("/buscar", response_model=list[PlomeroResponse])
def buscar(
    localidad:         Optional[str]  = None,
    genero:            Optional[str]  = None,
    especialidad:      Optional[str]  = None,
    atiende_urgencias: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    return plomero_service.buscar(db, localidad, genero, especialidad, atiende_urgencias)

@router.patch("/disponibilidad")
#no recibe el ID por URL sino que lo saca del token
def cambiar_disponibilidad(
    disponible: bool,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual)  # verifica el JWT
):
    return plomero_service.cambiar_disponibilidad(db, id_plomero, disponible)

@router.post("/olvide-password")
def olvide_password(datos: OlvidePasswordPlomeroRequest, db: Session = Depends(get_db)):
    return plomero_service.olvide_password(db, datos.email)

@router.post("/reset-password")
def reset_password(datos: ResetPasswordPlomeroRequest, db: Session = Depends(get_db)):
    return plomero_service.reset_password(db, datos.token, datos.nueva_password)


@router.get("/{id}", response_model=PlomeroResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    return plomero_service.obtener_por_id(db, id)