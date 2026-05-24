# core/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM

bearer = HTTPBearer()


def _verificar_token(credentials: HTTPAuthorizationCredentials, allowed_roles: list[str]) -> dict:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("tipo")

        if not user_id or role not in allowed_roles:
            raise HTTPException(status_code=403, detail="No autorizado")

        return {"id": int(user_id), "role": role}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


class _RoleChecker:
    def __init__(self, roles: list[str]):
        self.roles = roles

    def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> int:
        return _verificar_token(credentials, self.roles)["id"]


get_usuario_actual = _RoleChecker(["usuario"])
get_plomero_actual = _RoleChecker(["plomero"])