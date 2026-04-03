from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.plomero import PlomeroRequest, PlomeroResponse
from services import plomero_service

router = APIRouter(prefix="/plomeros", tags=["Plomeros"])

@router.post("/registro")
def registrar(datos: PlomeroRequest, db: Session = Depends(get_db)):
    return plomero_service.registrar(db, datos)

@router.get("/", response_model=list[PlomeroResponse])
def listar(db: Session = Depends(get_db)):
    return plomero_service.obtener_todos(db)

@router.get("/{id}", response_model=PlomeroResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    return plomero_service.obtener_por_id(db, id)

@router.patch("/{id}/disponibilidad")
def cambiar_disponibilidad(id: int, disponible: bool, db: Session = Depends(get_db)):
    return plomero_service.cambiar_disponibilidad(db, id, disponible)