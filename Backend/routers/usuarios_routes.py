from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.solicitud import Solicitud
from database import get_db
from schemas.auth import (RegistroRequest, LoginRequest, LoginResponse,
                          OlvidePasswordRequest, ResetPasswordRequest)
from schemas.usuario import UsuarioResponse
from services import auth_service
from repositories import usuario_repository
from utils.auth_plomeros import get_usuario_actual

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
# ── Auth ────────────────────────────────────────────────────
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

# ── Perfil ──────────────────────────────────────────────────
#Regla general en FastAPI: las rutas específicas siempre antes que las rutas con parámetros dinámicos
#Para ver editar perfil
@router.get("/perfil", response_model=UsuarioResponse)
def perfil(
    db:         Session = Depends(get_db),
    id_usuario: int     = Depends(get_usuario_actual)
):
    usuario = usuario_repository.buscar_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UsuarioResponse.model_validate(usuario)

@router.get("/{id}", response_model=UsuarioResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    usuario = usuario_repository.buscar_por_id(db, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UsuarioResponse.model_validate(usuario)

#------------------------------@router.get("/solicitudes/historial", response_model=list[SolicitudResponse])
def historial_solicitudes(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_usuario_actual)
):
    """
    Obtiene todas las solicitudes realizadas por el usuario actual,
    ordenadas desde la más reciente.
    """
    solicitudes = (
        db.query(Solicitud)
        .filter(Solicitud.id_usuario == id_usuario)
        .order_by(Solicitud.fecha.desc())
        .all()
    )
    
    # Podés incluir lógica para adjuntar datos del plomero si el estado es ACEPTADO/COMPLETADO
    return solicitudes