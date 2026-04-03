from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models.plomero import Plomero
from schemas.plomero import PlomeroRequest, PlomeroResponse
from repositories import plomero_repository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def registrar(db: Session, datos: PlomeroRequest) -> dict:
    if plomero_repository.buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo = Plomero(
        nombre            = datos.nombre,
        apellido          = datos.apellido,
        email             = datos.email,
        telefono          = datos.telefono,
        especialidad      = datos.especialidad,
        genero            = datos.genero,
        localidad         = datos.localidad,
        atiende_urgencias = datos.atiende_urgencias,
        matricula_gas     = datos.matricula_gas,
        password_hash     = pwd_context.hash(datos.password),
        disponible_ahora  = True,
        puntuacion        = 0.0,
        total_trabajos    = 0,
    )
    plomero = plomero_repository.crear_plomero(db, nuevo)
    return {"mensaje": "Plomero registrado correctamente", "id": plomero.id_plomero}

def obtener_todos(db: Session) -> list[PlomeroResponse]:
    plomeros = plomero_repository.listar_todos(db)
    return [PlomeroResponse.model_validate(p) for p in plomeros]

def obtener_por_id(db: Session, id: int) -> PlomeroResponse:
    plomero = plomero_repository.buscar_por_id(db, id)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    return PlomeroResponse.model_validate(plomero)

def cambiar_disponibilidad(db: Session, id: int, disponible: bool) -> dict:
    plomero = plomero_repository.actualizar_disponibilidad(db, id, disponible)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    estado = "disponible" if disponible else "no disponible"
    return {"mensaje": f"Plomero marcado como {estado}"}