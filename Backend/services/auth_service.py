# services/auth_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from models.usuario import Usuario
from schemas.auth import RegistroRequest, LoginRequest, LoginResponse
from repositories.usuario_repository import buscar_por_email, crear_usuario

SECRET_KEY = "plomeria_secreta_2024"  # en producción va en .env
ALGORITHM  = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _hashear(password: str) -> str:
    return pwd_context.hash(password)

def _verificar(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def _crear_token(id_usuario: int) -> str:
    expiracion = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": str(id_usuario), "exp": expiracion},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def registrar(db: Session, datos: RegistroRequest) -> dict:
    # Verificar que el email no esté en uso
    if buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_usuario = Usuario(
        nombre        = datos.nombre,
        apellido      = datos.apellido,
        email         = datos.email,
        password_hash = _hashear(datos.password),
        direccion     = datos.direccion,
        telefono      = datos.telefono,
        latitud       = datos.latitud,
        longitud      = datos.longitud,
    )
    usuario = crear_usuario(db, nuevo_usuario)
    return {"mensaje": "Usuario registrado correctamente", "id": usuario.id_usuario}

def login(db: Session, datos: LoginRequest) -> LoginResponse:
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