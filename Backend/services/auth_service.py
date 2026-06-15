# services/auth_service.py
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from utils.email import enviar_reset_password
from utils.seguridad import verify_password, hash_password, create_token
from repositories import usuario_repository, plomero_repository


def login(db: Session, email: str, password: str):

    # ── USUARIO ──────────────────────────────────────────────────────────────
    user = usuario_repository.buscar_por_email(db, email)

    if user and verify_password(password, user.password_hash):
        from services import moderacion
        moderacion.reactivar_si_corresponde(db, user)
        if moderacion.esta_suspendido(db, user):
            raise HTTPException(status_code=403, detail=moderacion.mensaje_suspension(user))
        token = create_token({"sub": str(user.id_usuario), "tipo": "usuario"})
        return {
            "access_token": token,
            "token_type":   "bearer",
            "id":           user.id_usuario,
            "nombre":       user.nombre,
            "apellido":     user.apellido,
            "email":        user.email,
            "localidad":    user.localidad,
            "direccion":    user.direccion,
            "latitud":      user.latitud,
            "longitud":     user.longitud,
            "tipo":         "usuario"
        }

    # ── PLOMERO ───────────────────────────────────────────────────────────────
    plomero = plomero_repository.buscar_por_email(db, email)

    if plomero and verify_password(password, plomero.password_hash):
        from services import moderacion
        moderacion.reactivar_si_corresponde(db, plomero)
        if moderacion.esta_suspendido(db, plomero):
            raise HTTPException(status_code=403, detail=moderacion.mensaje_suspension(plomero))
        token = create_token({"sub": str(plomero.id_plomero), "tipo": "plomero"})
        return {
            "access_token":    token,
            "token_type":      "bearer",
            "id":              plomero.id_plomero,
            "nombre":          plomero.nombre,
            "apellido":        plomero.apellido,
            "email":           plomero.email,
            "localidad":       plomero.localidad,
            "tipo":            "plomero",
            "disponible_ahora": plomero.disponible_ahora,
        }

    raise HTTPException(status_code=401, detail="Credenciales inválidas")


# ── FORGOT PASSWORD ───────────────────────────────────────────────────────────
def forgot_password(db: Session, email: str):
    user = usuario_repository.buscar_por_email(db, email)
    role = "usuario"
    if not user:
        user = plomero_repository.buscar_por_email(db, email)
        role = "plomero"
    if not user:
        return {"message": "Si el email existe, recibirás instrucciones"}

    from services import moderacion
    if moderacion.esta_suspendido(db, user):
        raise HTTPException(status_code=403, detail=moderacion.mensaje_suspension(user))

    token = secrets.token_urlsafe(32)
    if role == "usuario":
        usuario_repository.guardar_reset_token(db, user.id_usuario, token)
        email_to = user.email
    else:
        plomero_repository.guardar_reset_token(db, user.id_plomero, token)
        email_to = user.email

    try:
        enviar_reset_password(email_to, token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Si el email existe, recibirás instrucciones"}


# ── RESET PASSWORD ────────────────────────────────────────────────────────────
def reset_password(db: Session, token: str, new_password: str):
    from services import moderacion
    user = usuario_repository.buscar_por_reset_token(db, token)
    if user:
        if moderacion.esta_suspendido(db, user):
            raise HTTPException(status_code=403, detail=moderacion.mensaje_suspension(user))
        usuario_repository.actualizar_password(db, user.id_usuario, hash_password(new_password))
        return {"message": "Contraseña actualizada correctamente"}

    plomero = plomero_repository.buscar_por_reset_token(db, token)
    if plomero:
        if moderacion.esta_suspendido(db, plomero):
            raise HTTPException(status_code=403, detail=moderacion.mensaje_suspension(plomero))
        plomero_repository.actualizar_password(db, plomero.id_plomero, hash_password(new_password))
        return {"message": "Contraseña actualizada correctamente"}

    raise HTTPException(status_code=400, detail="Token inválido o expirado")
