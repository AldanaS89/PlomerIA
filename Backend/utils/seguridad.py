# utils/seguridad.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd.verify(password, hashed)


def create_token(data: dict, expires_hours: int = 24):
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)