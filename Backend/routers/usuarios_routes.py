from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.auth.usuario_auth import RegistroRequest
from services import auth_service
from schemas.usuario import UsuarioResponse
from database import get_db
from core.auth import get_usuario_actual
from services import usuarios_service

router = APIRouter(tags=["Usuarios"])


# ── AUTH ─────────────────────────────

@router.post("/registro")
def registrar(datos: RegistroRequest, db: Session = Depends(get_db)):
    return usuarios_service.registrar(db, datos)

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