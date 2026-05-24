# services/usuarios_service.py
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session


from schemas.auth.usuario_auth import RegistroRequest
from models.usuario import Usuario
from repositories import usuario_repository

from utils.seguridad import hash_password
from utils.geolocalizacion import geocodificar
from utils.seguridad import create_token



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


def obtener_perfil(db, id_usuario):
    usuario = usuario_repository.buscar_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario