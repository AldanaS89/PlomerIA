from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.auth.auth import LoginRequest, OlvidePasswordRequest, ResetPasswordRequest
from database import get_db
from services import auth_service


router = APIRouter(tags=["Auth"])


# ─────────────────────────────
# LOGIN UNIFICADO
# ─────────────────────────────
@router.post("/login")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, datos.email, datos.password)

# ─────────────────────────────
# FORGOT PASSWORD
# ─────────────────────────────
@router.post("/forgot-password")
def forgot_password(datos: OlvidePasswordRequest, db: Session = Depends(get_db)):
    return auth_service.forgot_password(db, datos.email)


# ─────────────────────────────
# RESET PASSWORD
# ─────────────────────────────
@router.post("/reset-password")
def reset_password(datos: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.reset_password(db, datos.token, datos.nueva_password)