# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from database import get_db
from models.usuario import Usuario

"""
Cuando un usuario hace login, el servidor le devuelve un token (una cadena larga de texto). Ese token es como un pase — cada vez que el usuario 
quiere hacer algo que requiere estar logueado, manda ese token en el header de la request. El servidor lo verifica y sabe quién es.
"""

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Configuración de seguridad
SECRET_KEY = "plomeria_secreta_2024"   # en producción esto va en .env
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Schemas (qué datos esperamos recibir) ──────────────────
class RegistroSchema(BaseModel):
    nombre: str
    apellido: str
    email: str
    password: str
    direccion: str
    telefono: str
    latitud: float
    longitud: float

class LoginSchema(BaseModel):
    email: str
    password: str

# ── Funciones auxiliares ───────────────────────────────────
def hashear_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)

def crear_token(datos: dict) -> str:
    datos["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

# ── Rutas ──────────────────────────────────────────────────
@router.post("/registro")
def registrar_usuario(datos: RegistroSchema, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    existe = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo = Usuario(
        nombre        = datos.nombre,
        apellido      = datos.apellido,
        email         = datos.email,
        password_hash = hashear_password(datos.password),
        direccion     = datos.direccion,
        telefono      = datos.telefono,
        latitud       = datos.latitud,
        longitud      = datos.longitud,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Usuario registrado correctamente", "id": nuevo.id_usuario}

@router.post("/login")
def login(datos: LoginSchema, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = crear_token({"sub": str(usuario.id_usuario), "tipo": "usuario"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
        }
    }