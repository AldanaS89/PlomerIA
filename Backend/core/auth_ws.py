from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM
from fastapi import HTTPException


def decode_token_ws(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return {
            "id": int(payload["sub"]),
            "role": payload["tipo"]
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")