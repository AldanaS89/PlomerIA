from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets

# Importamos configuración, modelos y repositorio
from config import SECRET_KEY, ALGORITHM
from models.plomero import Plomero
from schemas.plomero import (
    PlomeroRequest,
    PlomeroResponse,
    PlomeroLoginRequest,
    PlomeroLoginResponse,
    OlvidePasswordPlomeroRequest,
    ResetPasswordPlomeroRequest
)
from repositories import plomero_repository

# Usamos el esquema unificado pbkdf2_sha256 para evitar el error de los 72 bytes
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# ──────────────────────────────────────────────
# Helpers privados (consistentes con auth_service)
# ──────────────────────────────────────────────

def _hashear(password: str) -> str:
    """Genera un hash seguro compatible con el frontend."""
    return pwd_context.hash(password)

def _verificar(password: str, hashed: str) -> bool:
    """Verifica la contraseña contra el hash de la base de datos."""
    return pwd_context.verify(password, hashed)

def _crear_token(id_plomero: int) -> str:
    """Genera un JWT con el ID del plomero, tipo y expiración en 24hs."""
    expiracion = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": str(id_plomero), "tipo": "plomero", "exp": expiracion},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ──────────────────────────────────────────────
# Registro y Login
# ──────────────────────────────────────────────

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
        latitud           = datos.latitud,
        longitud          = datos.longitud,
        atiende_urgencias = datos.atiende_urgencias,
        matricula_gas     = datos.matricula_gas,
        password_hash     = _hashear(datos.password),
        disponible_ahora  = True,
        puntuacion        = 0.0,
        total_trabajos    = 0,
    )

    plomero = plomero_repository.crear_plomero(db, nuevo)
    token   = _crear_token(plomero.id_plomero)

    # UX mejorada: el plomero queda logueado al registrarse
    return {
        "mensaje":      "Plomero registrado correctamente",
        "access_token": token,
        "token_type":   "bearer",
        "id_plomero":   plomero.id_plomero,
        "nombre":       plomero.nombre,
    }

def login(db: Session, datos: PlomeroLoginRequest) -> PlomeroLoginResponse:
    plomero = plomero_repository.buscar_por_email(db, datos.email)

    if not plomero or not _verificar(datos.password, plomero.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = _crear_token(plomero.id_plomero)

    return PlomeroLoginResponse(
        access_token = token,
        token_type   = "bearer",
        id_plomero   = plomero.id_plomero,
        nombre       = plomero.nombre,
    )


# ──────────────────────────────────────────────
# Consultas
# ──────────────────────────────────────────────

def obtener_todos(db: Session) -> list[PlomeroResponse]:
    plomeros = plomero_repository.listar_todos(db)
    return [PlomeroResponse.model_validate(p) for p in plomeros]

def obtener_por_id(db: Session, id: int) -> PlomeroResponse:
    plomero = plomero_repository.buscar_por_id(db, id)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    return PlomeroResponse.model_validate(plomero)

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


# ──────────────────────────────────────────────
# Disponibilidad
# ──────────────────────────────────────────────

def cambiar_disponibilidad(db: Session, id: int, disponible: bool) -> dict:
    plomero = plomero_repository.actualizar_disponibilidad(db, id, disponible)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    estado = "disponible" if disponible else "no disponible"
    return {"mensaje": f"Plomero marcado como {estado}"}


# ──────────────────────────────────────────────
# Recuperación de contraseña
# ──────────────────────────────────────────────

def olvide_password(db: Session, email: str) -> dict:
    RESPUESTA_GENERICA = {"mensaje": "Si el email existe, recibirás un link de recuperación"}

    plomero = plomero_repository.buscar_por_email(db, email)
    if not plomero:
        return RESPUESTA_GENERICA

    token = secrets.token_urlsafe(32)
    plomero_repository.guardar_reset_token(db, plomero.id_plomero, token)

    # Aquí conectarás el email_service más adelante
    return RESPUESTA_GENERICA

def reset_password(db: Session, token: str, nueva_password: str) -> dict:
    plomero = plomero_repository.buscar_por_reset_token(db, token)
    if not plomero:
        raise HTTPException(status_code=400, detail="Token inválido o ya usado")

    nuevo_hash = _hashear(nueva_password)
    plomero_repository.actualizar_password(db, plomero.id_plomero, nuevo_hash)

    return {"mensaje": "Contraseña actualizada correctamente"}
