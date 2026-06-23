from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone

from config import SECRET_KEY, ALGORITHM


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─────────────────────────────
# PASSWORD
# ─────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# ─────────────────────────────
# JWT
# ─────────────────────────────
def create_token(data: dict, expires_hours: int = 168) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    payload.update({"exp": expire})

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)