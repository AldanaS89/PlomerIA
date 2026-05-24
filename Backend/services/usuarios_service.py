# services/usuarios_service.py
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from utils.email import enviar_reset_password
from models.usuario import Usuario
from repositories import usuario_repository
from schemas.auth import RegistroRequest

from utils.seguridad import hash_password
from utils.geolocalizacion import geocodificar
from utils.seguridad import create_token
from schemas.auth import LoginRequest, LoginResponse
from utils.seguridad import verify_password

def login(db: Session, datos: LoginRequest) -> LoginResponse:
    usuario = usuario_repository.buscar_por_email(db, datos.email)

    if not usuario or not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_token({"sub": str(usuario.id_usuario), "tipo": "usuario"})

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        id_usuario=usuario.id_usuario,
        nombre=usuario.nombre,
        rol=usuario.rol,
    )
# ─────────────────────────────
# REGISTRO
# ─────────────────────────────

def registrar(db: Session, datos: RegistroRequest):

    if usuario_repository.buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    lat, lng = geocodificar(datos.direccion, datos.localidad)

    usuario = Usuario(
        nombre=datos.nombre,
        apellido=datos.apellido,
        email=datos.email,
        password_hash=hash_password(datos.password),
        direccion=datos.direccion,
        localidad=datos.localidad,
        telefono=datos.telefono,
        latitud=lat,
        longitud=lng,
    )

    usuario = usuario_repository.crear_usuario(db, usuario)

    token = create_token({
        "sub": str(usuario.id_usuario),
        "tipo": "usuario"
    })

    return {
        "mensaje": "Usuario creado",
        "access_token": token
    }
# ─────────────────────────────
# RESET PASSWORD
# ─────────────────────────────

def olvide_password(
    db: Session,
    email: str
) -> dict:

    usuario = usuario_repository.buscar_por_email(
        db,
        email
    )

    if not usuario:
        return {
            "mensaje":
            "Si el email existe, vas a recibir un link para restablecer tu contraseña"
        }

    token = secrets.token_urlsafe(32)

    usuario_repository.guardar_reset_token(
        db,
        usuario.id_usuario,
        token
    )

    try:
        enviar_reset_password(
            usuario.email,
            token
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar el email: {str(e)}"
        )

    return {
        "mensaje":
        "Si el email existe, vas a recibir un link para restablecer tu contraseña"
    }


def reset_password(
    db: Session,
    token: str,
    nueva_password: str
) -> dict:

    usuario = usuario_repository.buscar_por_reset_token(
        db,
        token
    )

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="Token inválido o ya usado"
        )

    nuevo_hash = hash_password(
        nueva_password
    )

    usuario_repository.actualizar_password(
        db,
        usuario.id_usuario,
        nuevo_hash
    )

    return {
        "mensaje":
        "Contraseña actualizada correctamente"
    }

def obtener_perfil(db, id_usuario):
    usuario = usuario_repository.buscar_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario