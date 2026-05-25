import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from utils.email import enviar_reset_password
from utils.seguridad import verify_password, hash_password, create_token
from repositories import usuario_repository, plomero_repository


def login(db: Session, email: str, password: str):

    # ─────────────────────────────
    # USUARIO
    # ─────────────────────────────
    user = usuario_repository.buscar_por_email(db, email)

    if user and verify_password(password, user.password_hash):

        token = create_token({
            "sub":  str(user.id_usuario),
            "tipo": "usuario"
        })

        return {
            "access_token": token,
            "token_type":   "bearer",
            "id":           user.id_usuario,
            "nombre":       user.nombre,
            "tipo":         "usuario"
        }

    # ─────────────────────────────
    # PLOMERO
    # ─────────────────────────────
    plomero = plomero_repository.buscar_por_email(db, email)

    if plomero and verify_password(password, plomero.password_hash):

        token = create_token({
            "sub":  str(plomero.id_plomero),
            "tipo": "plomero"
        })

        return {
            "access_token":   token,
            "token_type":     "bearer",
            "id":             plomero.id_plomero,
            "nombre":         plomero.nombre,
            "tipo":           "plomero",
            "disponible_ahora": plomero.disponible_ahora
        }

    raise HTTPException(status_code=401, detail="Credenciales inválidas")


# ─────────────────────────────
# FORGOT PASSWORD (UNIFICADO)
# ─────────────────────────────
def forgot_password(db: Session, email: str):

    user = usuario_repository.buscar_por_email(db, email)
    role = "usuario"

    if not user:
        user = plomero_repository.buscar_por_email(db, email)
        role = "plomero"

    if not user:
        return {"message": "Si el email existe, recibirás instrucciones"}

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


# ─────────────────────────────
# RESET PASSWORD (UNIFICADO)
# ─────────────────────────────
def reset_password(db: Session, token: str, new_password: str):

    # ───── USUARIO ─────
    user = usuario_repository.buscar_por_reset_token(db, token)

    if user:
        new_hash = hash_password(new_password)
        usuario_repository.actualizar_password(db, user.id_usuario, new_hash)
        return {"message": "Contraseña actualizada correctamente"}

    # ───── PLOMERO ─────
    plomero = plomero_repository.buscar_por_reset_token(db, token)

    if plomero:
        new_hash = hash_password(new_password)
        plomero_repository.actualizar_password(db, plomero.id_plomero, new_hash)
        return {"message": "Contraseña actualizada correctamente"}

    raise HTTPException(status_code=400, detail="Token inválido o expirado")