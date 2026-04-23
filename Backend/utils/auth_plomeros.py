# utils/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()
"""
Esta función se usa como dependencia en el router con Depends(get_plomero_actual). Lo que hace es:
Toma el token del header Authorization: Bearer <token>
Lo decodifica con el SECRET_KEY
Verifica que sea un token de plomero (no de usuario)
Devuelve el id_plomero que está adentro del token
"""

def get_plomero_actual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
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
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> int:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("tipo") != "usuario":
            raise HTTPException(status_code=403, detail="No autorizado")
        return int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")