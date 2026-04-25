from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import secrets

# Importamos los modelos y esquemas necesarios
from models.usuario import Usuario
from schemas.auth import RegistroRequest, LoginRequest, LoginResponse
from repositories import usuario_repository 

SECRET_KEY = "plomeria_secreta_2024" 
ALGORITHM  = "HS256"

# Configuración de seguridad para contraseñas
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"], 
    deprecated="auto"
)

# --- FUNCIONES DE SEGURIDAD ---

def hashear_password(password: str) -> str:
    """Encripta la contraseña para guardarla de forma segura."""
    return pwd_context.hash(password)

def verificar_password(password: str, hashed: str) -> bool:
    """Compara una contraseña ingresada con la guardada en la base de datos."""
    return pwd_context.verify(password, hashed)

def crear_token(id_usuario: int) -> str:
    """Genera el token de acceso para que el usuario permanezca logueado."""
    expiracion = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": str(id_usuario), "tipo": "usuario", "exp": expiracion},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# --- FLUJO DE AUTENTICACIÓN ---

def registrar(db: Session, datos: RegistroRequest) -> dict:
    """Crea un nuevo usuario en la base de datos recreada."""
    # Verificamos si el mail ya existe
    if usuario_repository.buscar_por_email(db, datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # Creamos el objeto Usuario con los nuevos campos de tu rama
    nuevo_usuario = Usuario(
        nombre        = datos.nombre,
        apellido      = datos.apellido,
        email         = datos.email,
        password_hash = hashear_password(datos.password),
        direccion     = datos.direccion,
        localidad     = datos.localidad, # Campo clave para Almirante Brown
        telefono      = datos.telefono,
        latitud       = datos.latitud,
        longitud      = datos.longitud,
    )
    
    usuario = usuario_repository.crear_usuario(db, nuevo_usuario)
    return {"mensaje": "Usuario registrado correctamente", "id": usuario.id_usuario}

def login(db: Session, datos: LoginRequest) -> LoginResponse:
    """Valida las credenciales y devuelve el token de acceso."""
    usuario = usuario_repository.buscar_por_email(db, datos.email)

    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    # Generamos el token usando la función corregida
    token = crear_token(usuario.id_usuario)
    
    return LoginResponse(
        access_token = token,
        token_type   = "bearer",
        id_usuario   = usuario.id_usuario,
        nombre       = usuario.nombre,
    )
