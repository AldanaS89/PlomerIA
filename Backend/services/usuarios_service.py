# services/usuarios_service.py
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from schemas.auth.usuario_auth import RegistroRequest
from models.usuario import Usuario
from repositories import usuario_repository

from utils.seguridad import hash_password, create_token
from utils.geolocalizacion import geocodificar


# ─────────────────────────────
# REGISTRO
# ─────────────────────────────

def registrar(db: Session, datos: RegistroRequest):

    if usuario_repository.buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Usar las coordenadas del mapa si el usuario las confirmó; geocodificar
    # solo como respaldo (Nominatim falla/limita del lado del servidor y caería
    # al centroide genérico, dando distancias erróneas).
    if datos.latitud is not None and datos.longitud is not None:
        lat, lng = datos.latitud, datos.longitud
    else:
        lat, lng = geocodificar(datos.direccion, datos.localidad)

    usuario = Usuario(
        nombre        = datos.nombre,
        apellido      = datos.apellido,
        email         = datos.email,
        password_hash = hash_password(datos.password),
        direccion     = datos.direccion,
        localidad     = datos.localidad,
        # telefono eliminado — reemplazado por mensajería interna
        latitud       = lat,
        longitud      = lng,
    )

    usuario = usuario_repository.crear_usuario(db, usuario)

    token = create_token({
        "sub":  str(usuario.id_usuario),
        "tipo": "usuario"
    })

    return {
        "mensaje":       "Usuario creado",
        "access_token":  token
    }


# ─────────────────────────────
# PERFIL
# ─────────────────────────────

def obtener_perfil(db, id_usuario):
    usuario = usuario_repository.buscar_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario