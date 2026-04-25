from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import secrets

from config import SECRET_KEY, ALGORITHM
from models.usuario import Usuario
from schemas.auth import RegistroRequest, LoginRequest, LoginResponse
from repositories import usuario_repository
from repositories.usuario_repository import (
    buscar_por_email,
    crear_usuario,
)
from services.email_service import enviar_reset_password  # ajustá el import a tu estructura

# pbkdf2_sha256: sin el bug de 72 bytes de bcrypt, compatible con el frontend
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# ──────────────────────────────────────────────
# Helpers privados
# ──────────────────────────────────────────────

def _hashear(password: str) -> str:
    """Genera un hash seguro para la contraseña."""
    return pwd_context.hash(password)


def _verificar(password: str, hashed: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash guardado."""
    return pwd_context.verify(password, hashed)


def _crear_token(id_usuario: int, tipo: str = "usuario") -> str:
    """Genera un JWT con 24 horas de vigencia."""
    expiracion = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": str(id_usuario), "tipo": tipo, "exp": expiracion},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ──────────────────────────────────────────────
# Registro
# ──────────────────────────────────────────────

def registrar(db: Session, datos: RegistroRequest) -> dict:
    """
    Registra un nuevo usuario.
    Devuelve el token directamente para que el frontend pueda
    iniciar sesión sin un paso extra (mejor UX).
    """
    if buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_usuario = Usuario(
        nombre        = datos.nombre,
        apellido      = datos.apellido,
        email         = datos.email,
        password_hash = _hashear(datos.password),
        localidad     = datos.localidad,   # compatibilidad frontend
        direccion     = datos.direccion,   # para GeoPy
        telefono      = datos.telefono,
        latitud       = datos.latitud,     # radio de 5 km
        longitud      = datos.longitud,    # radio de 5 km
    )

    usuario = crear_usuario(db, nuevo_usuario)
    token   = _crear_token(usuario.id_usuario)

    # Devolvemos el token en el registro → el usuario queda logueado de una
    return {
        "mensaje":      "Usuario registrado correctamente",
        "access_token": token,
        "token_type":   "bearer",
        "id_usuario":   usuario.id_usuario,
        "nombre":       usuario.nombre,
    }


# ──────────────────────────────────────────────
# Login
# ──────────────────────────────────────────────

def login(db: Session, datos: LoginRequest) -> LoginResponse:
    """Valida credenciales y devuelve el token con los datos del usuario."""
    usuario = buscar_por_email(db, datos.email)

    if not usuario or not _verificar(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = _crear_token(usuario.id_usuario)

    return LoginResponse(
        access_token = token,
        token_type   = "bearer",
        id_usuario   = usuario.id_usuario,
        nombre       = usuario.nombre,
    )


# ──────────────────────────────────────────────
# Recuperación de contraseña
# ──────────────────────────────────────────────

def olvide_password(db: Session, email: str) -> dict:
    """
    Siempre devuelve el mismo mensaje para no revelar
    si el email existe o no (seguridad).
    """
    RESPUESTA_GENERICA = {
        "mensaje": "Si el email existe, vas a recibir un link para restablecer tu contraseña"
    }

    usuario = buscar_por_email(db, email)
    if not usuario:
        return RESPUESTA_GENERICA

    token = secrets.token_urlsafe(32)
    usuario_repository.guardar_reset_token(db, usuario.id_usuario, token)

    try:
        enviar_reset_password(usuario.email, token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el email: {str(e)}")

    return RESPUESTA_GENERICA


def reset_password(db: Session, token: str, nueva_password: str) -> dict:
    """Actualiza la contraseña usando el token de recuperación."""
    usuario = usuario_repository.buscar_por_reset_token(db, token)

    if not usuario:
        raise HTTPException(status_code=400, detail="Token inválido o ya usado")

    nuevo_hash = _hashear(nueva_password)
    usuario_repository.actualizar_password(db, usuario.id_usuario, nuevo_hash)

    return {"mensaje": "Contraseña actualizada correctamente"}