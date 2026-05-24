from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from core.auth import get_usuario_actual
from services import usuarios_service
from schemas.auth import *
from schemas.usuario import UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# ── AUTH ─────────────────────────────

@router.post("/registro")
def registrar(datos: RegistroRequest, db: Session = Depends(get_db)):
    return usuarios_service.registrar(db, datos)


@router.post("/login", response_model=LoginResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    return usuarios_service.login(db, datos)


@router.post("/olvide-password")
def olvide_password(datos: OlvidePasswordRequest, db: Session = Depends(get_db)):
    return usuarios_service.olvide_password(db, datos.email)


@router.post("/reset-password")
def reset_password(datos: ResetPasswordRequest, db: Session = Depends(get_db)):
    return usuarios_service.reset_password(db, datos.token, datos.nueva_password)


# ── PERFIL ─────────────────────────────

@router.get("/me", response_model=UsuarioResponse)
def perfil(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual),
):
    return usuarios_service.obtener_perfil(db, id_usuario)


@router.get("/{id}", response_model=UsuarioResponse)
def obtener(
    id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_usuario_actual),  # protección base
):
    return usuarios_service.obtener_perfil(db, id)