# Backend/utils/seguridad.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM

# Configurador de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_password(password_plana: str, password_hasheada: str) -> bool:
    """Compara la clave ingresada con el hash de la base de datos"""
    return pwd_context.verify(password_plana, password_hasheada)

def hashear_password(password: str) -> str:
    """Convierte la clave en un hash irreversible"""
    return pwd_context.hash(password)

def crear_token_acceso(data: dict, expires_delta: timedelta = None):
    """Crea el token JWT incluyendo el campo 'tipo' y expiración precisa"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=1440) # 24 horas
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)