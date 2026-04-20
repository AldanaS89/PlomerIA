# routers/solicitudes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.solicitud import SolicitudCreate, SolicitudResponse
from services import solicitud_service
from utils.auth_plomeros import get_usuario_actual

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])

@router.post("/", response_model=SolicitudResponse)
def crear(
    datos: SolicitudCreate,
    db: Session = Depends(get_db),
    # Esta función extrae el ID del token que pegaste en el candadito
    id_usuario_conectado: int = Depends(get_usuario_actual)
):
    """
    Crea una nueva solicitud de plomería.
    El id_usuario se toma automáticamente del token de seguridad.
    """
    try:
        return solicitud_service.crear_solicitud(db, datos, id_usuario_conectado)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/mis-solicitudes", response_model=list[SolicitudResponse])
def listar_mis_pedidos(
    db: Session = Depends(get_db),
    id_usuario_conectado: int = Depends(get_usuario_actual)
):
    """
    Trae solo las solicitudes que creaste vos.
    """
    return solicitud_service.listar_por_usuario_s(db, id_usuario_conectado)

@router.get("/{id_solicitud}", response_model=SolicitudResponse)
def obtener_detalle(
    id_solicitud: int, 
    db: Session = Depends(get_db),
    id_usuario_conectado: int = Depends(get_usuario_actual)
):
    """
    Obtiene el detalle de una solicitud específica.
    """
    solicitud = solicitud_service.obtener_por_id_s(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return solicitud