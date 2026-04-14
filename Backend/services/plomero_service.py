from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

from config import SECRET_KEY, ALGORITHM
from models.plomero import Plomero
from schemas.plomero import (
    PlomeroRequest,
    PlomeroResponse,
    PlomeroLoginRequest,
    PlomeroLoginResponse,
)
from repositories import plomero_repository

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def registrar(db: Session, datos: PlomeroRequest) -> dict:
    if plomero_repository.buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    nuevo = Plomero(
        nombre=datos.nombre,
        apellido=datos.apellido,
        email=datos.email,
        telefono=datos.telefono,
        especialidad=datos.especialidad,
        genero=datos.genero,
        localidad=datos.localidad,
        atiende_urgencias=datos.atiende_urgencias,
        matricula_gas=datos.matricula_gas,
        password_hash=pwd_context.hash(datos.password),
        disponible_ahora=True,
        puntuacion=0.0,
        total_trabajos=0,
    )
    plomero = plomero_repository.crear_plomero(db, nuevo)
    return {"mensaje": "Plomero registrado correctamente", "id": plomero.id_plomero}


def _crear_token(id_plomero: int) -> str:
    expiracion = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": str(id_plomero), "tipo": "plomero", "exp": expiracion},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def login(db: Session, datos: PlomeroLoginRequest) -> PlomeroLoginResponse:
    plomero = plomero_repository.buscar_por_email(db, datos.email)
    if not plomero or not pwd_context.verify(datos.password, plomero.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    token = _crear_token(plomero.id_plomero)
    return PlomeroLoginResponse(
        access_token=token,
        token_type="bearer",
        id_plomero=plomero.id_plomero,
        nombre=plomero.nombre,
    )


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


def buscar(
    db: Session,
    localidad: Optional[str] = None,
    genero: Optional[str] = None,
    especialidad: Optional[str] = None,
    atiende_urgencias: Optional[bool] = None,
) -> list[PlomeroResponse]:
    plomeros = plomero_repository.filtrar(
        db, localidad, genero, especialidad, atiende_urgencias
    )
    return [PlomeroResponse.model_validate(p) for p in plomeros]
