from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets
from models.plomero import Plomero
from utils.email import enviar_reset_password
from schemas.plomero import (PlomeroRequest, PlomeroResponse,
                              PlomeroLoginRequest, PlomeroLoginResponse, OlvidePasswordPlomeroRequest, ResetPasswordPlomeroRequest)
from repositories import plomero_repository
from config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _crear_token(id_plomero: int) -> str:
    """Genera un JWT con el ID del plomero, tipo y expiración en 24hs."""
    expiracion = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": str(id_plomero), "tipo": "plomero", "exp": expiracion},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def registrar(db: Session, datos: PlomeroRequest) -> dict:
    if plomero_repository.buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo = Plomero(
        nombre            = datos.nombre,
        apellido          = datos.apellido,
        email             = datos.email,
        telefono          = datos.telefono,
        especialidad      = datos.especialidad.value, # .value convierte el enum a string
        otra_especialidad = datos.otra_especialidad,
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
    token   = _crear_token(plomero.id_plomero)

    return {
        "mensaje":      "Plomero registrado correctamente",
        "access_token": token,
        "token_type":   "bearer",
        "id_plomero":   plomero.id_plomero,
        "nombre":       plomero.nombre,
    }

def login(db: Session, datos: PlomeroLoginRequest) -> PlomeroLoginResponse:
    plomero = plomero_repository.buscar_por_email(db, datos.email)
    if not plomero or not pwd_context.verify(datos.password, plomero.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = _crear_token(plomero.id_plomero)
    return PlomeroLoginResponse(
        access_token = token,
        token_type   = "bearer",
        id_plomero   = plomero.id_plomero,
        nombre       = plomero.nombre,
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
    db:                Session,
    localidad:         Optional[str]  = None,
    genero:            Optional[str]  = None,
    especialidad:      Optional[str]  = None,
    atiende_urgencias: Optional[bool] = None,
) -> list[PlomeroResponse]:
    plomeros = plomero_repository.filtrar(
        db, localidad, genero, especialidad, atiende_urgencias
    )
    return [PlomeroResponse.model_validate(p) for p in plomeros]

def olvide_password(db: Session, email: str) -> dict:
    plomero = plomero_repository.buscar_por_email(db, email)

    if not plomero:
        return {"mensaje": "Si el email existe, vas a recibir un link para restablecer tu contraseña"}

    token = secrets.token_urlsafe(32)
    plomero_repository.guardar_reset_token(db, plomero.id_plomero, token)

    try:
        enviar_reset_password(plomero.email, token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el email: {str(e)}")

    return {"mensaje": "Si el email existe, vas a recibir un link para restablecer tu contraseña"}

def reset_password(db: Session, token: str, nueva_password: str) -> dict:
    plomero = plomero_repository.buscar_por_reset_token(db, token)
    if not plomero:
        raise HTTPException(status_code=400, detail="Token inválido o ya usado")

    nuevo_hash = pwd_context.hash(nueva_password)
    plomero_repository.actualizar_password(db, plomero.id_plomero, nuevo_hash)

    return {"mensaje": "Contraseña actualizada correctamente"}