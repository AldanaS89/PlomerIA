from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM

bearer = HTTPBearer()


# ─────────────────────────────
# DECODE TOKEN
# ─────────────────────────────
def decode_token(credentials, allowed_roles):
    token = credentials.credentials

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    user_id = payload.get("sub")
    role = payload.get("tipo")

    if not user_id or not role:
        raise HTTPException(401, "Token inválido")

    if role not in allowed_roles:
        raise HTTPException(403, "No autorizado")

    return {"id": int(user_id), "role": role}


# ─────────────────────────────
# FACTORY DE ROLES
# ─────────────────────────────
def require_role(roles: list[str]):
    def wrapper(
        credentials: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> int:
        return decode_token(credentials, roles)["id"]

    return wrapper


# ─────────────────────────────
# ACTOR GENÉRICO (cualquiera de los dos roles)
# Devuelve {id, role} — útil para recursos compartidos como
# notificaciones y mensajería, donde importan ambos.
# ─────────────────────────────
def get_actor_actual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:
    return decode_token(credentials, ["usuario", "plomero"])


# ─────────────────────────────
# DEPENDENCIES LISTAS
# ─────────────────────────────
get_usuario_actual = require_role(["usuario"])
get_plomero_actual = require_role(["plomero"])