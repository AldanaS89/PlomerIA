from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.solicitud import EstadoSolicitud
from repositories import solicitud_repository, usuario_repository
from services.ia_service import analizar_descripcion
from services import filtrado_service, notificacion_service

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.solicitud import EstadoSolicitud
from schemas.solicitud import SolicitudCreate, SolicitudResponse

from repositories import (
    solicitud_repository,
    usuario_repository,
    plomero_repository
)

from services import ia_service


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _to_response(s) -> SolicitudResponse:
    return SolicitudResponse.model_validate(s)


def chat_habilitado(solicitud) -> bool:
    """
    Regla única del sistema de chat:
    SOLO se habilita cuando el plomero está trabajando.
    """
    return solicitud.estado == EstadoSolicitud.EN_PROGRESO


# ─────────────────────────────────────────────
# CREAR SOLICITUD
# ─────────────────────────────────────────────
def crear_solicitud(db: Session, datos: SolicitudCreate, id_usuario: int):

    diagnostico = ia_service.analizar_descripcion(datos.descripcion_raw)

    usuario = usuario_repository.buscar_por_id(db, id_usuario)
    localidad = usuario.localidad if usuario else None

    # 1. buscar plomero automáticamente
    plomero = plomero_repository.buscar_disponible_para(
        db,
        especialidad=diagnostico["etiqueta_ia"],
        localidad=localidad,
        atiende_urgencias=(diagnostico["urgencia_ia"] == "URGENTE"),
    )

    # fallback
    if not plomero:
        plomero = plomero_repository.buscar_disponible_para(
            db,
            especialidad=diagnostico["etiqueta_ia"]
        )

    if not plomero:
        plomero = plomero_repository.buscar_disponible_para(db)

    # 2. crear solicitud con o sin plomero
    solicitud = solicitud_repository.crear(
        db,
        id_usuario,
        datos,
        diagnostico
    )

    if plomero:
        solicitud.id_plomero = plomero.id_plomero
        solicitud.estado = EstadoSolicitud.EN_PROGRESO
    else:
        solicitud.estado = EstadoSolicitud.PENDIENTE

    db.commit()
    db.refresh(solicitud)

    return _to_response(solicitud)

# ─────────────────────────────────────────────
# OBTENER
# ─────────────────────────────────────────────

def obtener_por_id(db: Session, id_solicitud: int):
    s = solicitud_repository.obtener_por_id(db, id_solicitud)
    return _to_response(s) if s else None


def obtener_para_usuario(db: Session, id_solicitud: int, id_usuario: int):

    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")

    if solicitud.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="Sin acceso")

    return _to_response(solicitud)


# ─────────────────────────────────────────────
# LISTADOS
# ─────────────────────────────────────────────

def listar_por_usuario(db: Session, id_usuario: int):
    return [
        _to_response(s)
        for s in solicitud_repository.listar_por_usuario(db, id_usuario)
    ]


def listar_por_plomero(db: Session, id_plomero: int):
    return [
        _to_response(s)
        for s in solicitud_repository.listar_por_plomero(db, id_plomero)
    ]


# ─────────────────────────────────────────────
# ASIGNAR + INICIAR TRABAJO (CHAT SE ABRE ACÁ)
# ─────────────────────────────────────────────

def aceptar(db: Session, id_solicitud: int, id_plomero: int):

    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")

    if solicitud.id_plomero and solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=400, detail="Ya tomada por otro plomero")

    # asignar plomero
    solicitud_repository.asignar_plomero(db, id_solicitud, id_plomero)

    # activar estado de trabajo (CHAT SE HABILITA ACÁ)
    solicitud = solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.EN_PROGRESO
    )

    return _to_response(solicitud)


# ─────────────────────────────────────────────
# RECHAZAR
# ─────────────────────────────────────────────

def rechazar(db: Session, id_solicitud: int, id_plomero: int):

    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")

    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")

    solicitud = solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.RECHAZADO
    )

    return _to_response(solicitud)


# ─────────────────────────────────────────────
# COMPLETAR (CIERRA CHAT)
# ─────────────────────────────────────────────

def completar(db: Session, id_solicitud: int, id_plomero: int):

    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")

    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")

    if solicitud.estado != EstadoSolicitud.EN_PROGRESO:
        raise HTTPException(status_code=400, detail="No está en progreso")

    solicitud = solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.COMPLETADA
    )

    return _to_response(solicitud)


# ─────────────────────────────────────────────
# CANCELAR (CLIENTE)
# ─────────────────────────────────────────────

def cancelar(db: Session, id_solicitud: int, id_usuario: int):

    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")

    if solicitud.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="Sin acceso")

    if solicitud.estado == EstadoSolicitud.EN_PROGRESO:
        raise HTTPException(status_code=400, detail="No se puede cancelar en progreso")

    solicitud = solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.CANCELADA
    )

    return {
        "mensaje": "Solicitud cancelada",
        "estado": solicitud.estado.value
    }


# ─────────────────────────────────────────────
# BUSCAR
# ─────────────────────────────────────────────

def buscar_por_texto(db: Session, q: str):
    return solicitud_repository.buscar_por_texto(db, q)