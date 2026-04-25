from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import RegistroRequest, LoginRequest, LoginResponse, OlvidePasswordRequest,ResetPasswordRequest
from services import auth_service
from services.auth_service import hashear_password
from models import Usuario
from schemas.auth import OlvidePasswordRequest, ResetPasswordRequest

SECRET_KEY = "plomeria_secreta_2024"
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/registro")
def registrar(datos: RegistroRequest, db: Session = Depends(get_db)):
    return auth_service.registrar(db, datos)

@router.post("/login", response_model=LoginResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, datos)

@router.post("/olvide-password")
def olvide_password(datos: OlvidePasswordRequest, db: Session = Depends(get_db)):
    return auth_service.olvide_password(db, datos.email)

@router.post("/reset-password")
def reset_password(datos: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.reset_password(db, datos.token, datos.nueva_password)


