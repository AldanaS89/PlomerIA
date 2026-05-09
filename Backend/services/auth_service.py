# services/auth_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from config import SECRET_KEY, ALGORITHM   # ← FIX: misma fuente que auth_plomeros.py

from models.usuario import Usuario
from schemas.auth import RegistroRequest, LoginRequest, LoginResponse
from repositories import usuario_repository

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _geocodificar(direccion: str, localidad: str) -> tuple[float, float]:
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="plomeria_app_v1")
        query = f"{direccion}, {localidad}, Buenos Aires, Argentina"
        location = geolocator.geocode(query, timeout=5)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"[auth_service] Geopy falló, usando fallback: {e}")
    return -34.8116, -58.3967  # centroide Almirante Brown


def hashear_password(password: str) -> str:
    return pwd_context.hash(password)


def verificar_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def crear_token(id_usuario: int) -> str:
    expiracion = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": str(id_usuario), "tipo": "usuario", "exp": expiracion},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def registrar(db: Session, datos: RegistroRequest) -> dict:
    if usuario_repository.buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    latitud, longitud = _geocodificar(datos.direccion, datos.localidad)

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        apellido=datos.apellido,
        email=datos.email,
        password_hash=hashear_password(datos.password),
        direccion=datos.direccion,
        localidad=datos.localidad,
        telefono=datos.telefono,
        latitud=latitud,
        longitud=longitud,
    )

    usuario = usuario_repository.crear_usuario(db, nuevo_usuario)
    return {"mensaje": "Usuario registrado correctamente", "id": usuario.id_usuario}


def login(db: Session, datos: LoginRequest) -> LoginResponse:
    usuario = usuario_repository.buscar_por_email(db, datos.email)

    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = crear_token(usuario.id_usuario)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        id_usuario=usuario.id_usuario,
        nombre=usuario.nombre,
    )