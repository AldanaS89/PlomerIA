from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()


def get_plomero_actual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("tipo") != "plomero":
            raise HTTPException(status_code=403, detail="No autorizado")
        return int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


def get_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("tipo") != "usuario":
            raise HTTPException(status_code=403, detail="No autorizado")
        return int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
