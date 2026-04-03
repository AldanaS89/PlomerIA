# routers/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import RegistroRequest, LoginRequest, LoginResponse
from services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/registro")
def registrar(datos: RegistroRequest, db: Session = Depends(get_db)):
    return auth_service.registrar(db, datos)

@router.post("/login", response_model=LoginResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, datos)