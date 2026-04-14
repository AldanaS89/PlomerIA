# routers/solicitudes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.solicitud import SolicitudCreate, SolicitudResponse
from services import solicitud_service
from utils.auth_plomeros import get_usuario_actual, get_plomero_actual

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


@router.post("/", response_model=SolicitudResponse)
def crear(
    datos: SolicitudCreate,
    db: Session = Depends(get_db),
    id_usuario_conectado: int = Depends(get_usuario_actual),
):
    """Crea una solicitud. El diagnóstico IA y la asignación son automáticos."""
    try:
        return solicitud_service.crear_solicitud(db, datos, id_usuario_conectado)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/mis-solicitudes", response_model=list[SolicitudResponse])
def listar_mis_pedidos(
    db: Session = Depends(get_db),
    id_usuario_conectado: int = Depends(get_usuario_actual),
):
    return solicitud_service.listar_por_usuario_s(db, id_usuario_conectado)


@router.get("/asignadas", response_model=list[SolicitudResponse])
def listar_asignadas(
    db: Session = Depends(get_db),
    id_plomero_conectado: int = Depends(get_plomero_actual),
):
    """Solicitudes asignadas al plomero logueado."""
    return solicitud_service.listar_por_plomero_s(db, id_plomero_conectado)


@router.patch("/{id_solicitud}/aceptar", response_model=SolicitudResponse)
def aceptar(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero_conectado: int = Depends(get_plomero_actual),
):
    return solicitud_service.aceptar(db, id_solicitud, id_plomero_conectado)


@router.patch("/{id_solicitud}/rechazar", response_model=SolicitudResponse)
def rechazar(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_plomero_conectado: int = Depends(get_plomero_actual),
):
    return solicitud_service.rechazar(db, id_solicitud, id_plomero_conectado)


@router.get("/{id_solicitud}", response_model=SolicitudResponse)
def obtener_detalle(
    id_solicitud: int,
    db: Session = Depends(get_db),
    id_usuario_conectado: int = Depends(get_usuario_actual),
):
    solicitud = solicitud_service.obtener_por_id_s(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return solicitud
