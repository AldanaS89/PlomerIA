from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import secrets

from models.usuario import Usuario
from schemas.auth import RegistroRequest, LoginRequest, LoginResponse
from repositories import usuario_repository
from utils.email import enviar_reset_password
from config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashear_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def crear_token(id_usuario: int) -> str:
    expiracion = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": str(id_usuario), "tipo": "usuario", "exp": expiracion},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def registrar(db: Session, datos: RegistroRequest) -> dict:
    if usuario_repository.buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo = Usuario(
        nombre        = datos.nombre,
        apellido      = datos.apellido,
        email         = datos.email,
        password_hash = hashear_password(datos.password),
        direccion     = datos.direccion,
        telefono      = datos.telefono,
        latitud       = datos.latitud,
        longitud      = datos.longitud,
    )
    usuario = usuario_repository.crear_usuario(db, nuevo)
    token   = crear_token(usuario.id_usuario)

    return {
        "mensaje":      "Usuario registrado correctamente",
        "access_token": token,
        "token_type":   "bearer",
        "id_usuario":   usuario.id_usuario,
        "nombre":       usuario.nombre,
    }

def login(db: Session, datos: LoginRequest) -> LoginResponse:
    usuario = usuario_repository.buscar_por_email(db, datos.email)
    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = crear_token(usuario.id_usuario)
    return LoginResponse(
        access_token = token,
        token_type   = "bearer",
        id_usuario   = usuario.id_usuario,
        nombre       = usuario.nombre,
    )

def olvide_password(db: Session, email: str) -> dict:
    usuario = usuario_repository.buscar_por_email(db, email)

    if not usuario:
        return {"mensaje": "Si el email existe, vas a recibir un link para restablecer tu contraseña"}

    token = secrets.token_urlsafe(32)
    usuario_repository.guardar_reset_token(db, usuario.id_usuario, token)

    try:
        enviar_reset_password(usuario.email, token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el email: {str(e)}")

    return {"mensaje": "Si el email existe, vas a recibir un link para restablecer tu contraseña"}

def reset_password(db: Session, token: str, nueva_password: str) -> dict:
    usuario = usuario_repository.buscar_por_reset_token(db, token)
    if not usuario:
        raise HTTPException(status_code=400, detail="Token inválido o ya usado")

    nuevo_hash = pwd_context.hash(nueva_password)
    usuario_repository.actualizar_password(db, usuario.id_usuario, nuevo_hash)

    return {"mensaje": "Contraseña actualizada correctamente"}