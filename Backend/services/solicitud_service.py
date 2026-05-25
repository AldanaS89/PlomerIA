# services/solicitud_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from models.solicitud import EstadoSolicitud
from models.bloqueHorario import BloqueHorario
from schemas.solicitud import SolicitudCreate, SolicitudResponse

from repositories import (
    solicitud_repository,
    usuario_repository,
    plomero_repository,
)

from services import ia_service


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _to_response(s) -> SolicitudResponse:
    return SolicitudResponse.model_validate(s)


def chat_habilitado(solicitud) -> bool:
    """
    El chat solo se habilita cuando el plomero está trabajando.
    Se cierra cuando pasa a PENDIENTE_CALIFICACION.
    """
    return solicitud.estado == EstadoSolicitud.EN_PROGRESO


def _marcar_bloque_ocupado(
    db: Session,
    id_plomero: int,
    fecha_trabajo: datetime | None
) -> None:
    """
    Marca como ocupado el bloque horario del plomero
    que coincide con la fecha del trabajo aceptado.
    Si no hay bloque coincidente no rompe el flujo.
    """
    if not fecha_trabajo:
        return
    try:
        bloque = (
            db.query(BloqueHorario)
            .filter(
                BloqueHorario.id_plomero == id_plomero,
                BloqueHorario.inicio     <= fecha_trabajo,
                BloqueHorario.fin        >= fecha_trabajo,
                BloqueHorario.ocupado    == False,
            )
            .first()
        )
        if bloque:
            bloque.ocupado = True
            db.commit()
    except Exception as e:
        print(f"[solicitud_service] No se pudo marcar bloque: {e}")


# ─────────────────────────────────────────────
# CREAR SOLICITUD
# ─────────────────────────────────────────────

def crear_solicitud(db: Session, datos: SolicitudCreate, id_usuario: int):

    diagnostico = ia_service.analizar_descripcion(datos.descripcion_raw)

    usuario   = usuario_repository.buscar_por_id(db, id_usuario)
    localidad = usuario.localidad if usuario else None

    # Buscar plomero con fallback en 3 niveles
    # buscar_para_solicitud devuelve lista — tomamos el primero
    resultado = plomero_repository.buscar_para_solicitud(
        db,
        especialidades    = diagnostico["etiqueta_ia"],
        atiende_urgencias = (diagnostico["urgencia_ia"] == "URGENTE"),
    )
    plomero = resultado[0] if resultado else None

    if not plomero:
        resultado = plomero_repository.buscar_para_solicitud(
            db, especialidades=diagnostico["etiqueta_ia"]
        )
        plomero = resultado[0] if resultado else None

    if not plomero:
        resultado = plomero_repository.buscar_para_solicitud(db)
        plomero = resultado[0] if resultado else None

    # Crear solicitud
    solicitud = solicitud_repository.crear(db, id_usuario, datos, diagnostico)

    if plomero:
        solicitud.id_plomero = plomero.id_plomero
        solicitud.estado     = EstadoSolicitud.EN_PROGRESO
        _marcar_bloque_ocupado(db, plomero.id_plomero, solicitud.fecha)
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
# ACEPTAR — CHAT SE ABRE ACÁ
# ─────────────────────────────────────────────

# def aceptar(db: Session, id_solicitud: int, id_plomero: int):

#     solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

#     if not solicitud:
#         raise HTTPException(status_code=404, detail="No encontrada")

#     if solicitud.id_plomero and solicitud.id_plomero != id_plomero:
#         raise HTTPException(
#             status_code=400,
#             detail="Ya tomada por otro plomero"
#         )

#     solicitud_repository.asignar_plomero(db, id_solicitud, id_plomero)
#     solicitud = solicitud_repository.cambiar_estado(
#         db, id_solicitud, EstadoSolicitud.EN_PROGRESO
#     )

#     _marcar_bloque_ocupado(db, id_plomero, solicitud.fecha)

#     return _to_response(solicitud)


# # ─────────────────────────────────────────────
# # RECHAZAR
# # ─────────────────────────────────────────────

# def rechazar(db: Session, id_solicitud: int, id_plomero: int):

#     solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

#     if not solicitud:
#         raise HTTPException(status_code=404, detail="No encontrada")

#     if solicitud.id_plomero != id_plomero:
#         raise HTTPException(status_code=403, detail="No autorizado")

#     solicitud = solicitud_repository.cambiar_estado(
#         db, id_solicitud, EstadoSolicitud.CANCELADA
#     )

#     return _to_response(solicitud)


# # ─────────────────────────────────────────────
# # COMPLETAR — CHAT SE CIERRA, ESPERA CALIFICACIÓN
# # ─────────────────────────────────────────────

# def completar(db: Session, id_solicitud: int, id_plomero: int):

#     solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

#     if not solicitud:
#         raise HTTPException(status_code=404, detail="No encontrada")

#     if solicitud.id_plomero != id_plomero:
#         raise HTTPException(status_code=403, detail="No autorizado")

#     if solicitud.estado != EstadoSolicitud.EN_PROGRESO:
#         raise HTTPException(
#             status_code=400,
#             detail="No está en progreso"
#         )

#     solicitud = solicitud_repository.cambiar_estado(
#         db, id_solicitud, EstadoSolicitud.PENDIENTE_CALIFICACION
#     )

#     return _to_response(solicitud)

# # ─────────────────────────────────────────────
# # CANCELAR — CLIENTE
# # ─────────────────────────────────────────────

# def cancelar(db: Session, id_solicitud: int, id_usuario: int):

#     solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

#     if not solicitud:
#         raise HTTPException(status_code=404, detail="No encontrada")

#     if solicitud.id_usuario != id_usuario:
#         raise HTTPException(status_code=403, detail="Sin acceso")

#     if solicitud.estado == EstadoSolicitud.EN_PROGRESO:
#         raise HTTPException(
#             status_code=400,
#             detail="No se puede cancelar un trabajo en progreso"
#         )

#     solicitud = solicitud_repository.cambiar_estado(
#         db, id_solicitud, EstadoSolicitud.CANCELADA
#     )

#     return {
#         "mensaje": "Solicitud cancelada",
#         "estado":  solicitud.estado.value
#     }

def aceptar(db: Session, id_solicitud: int, id_plomero: int):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.estado != EstadoSolicitud.PENDIENTE:
        raise HTTPException(status_code=400, detail="La solicitud ya no está disponible")

    solicitud_repository.asignar_plomero(db, id_solicitud, id_plomero)
    _marcar_bloque_ocupado(db, id_plomero, solicitud.fecha)

    # Directo a EN_PROGRESO — saltea ASIGNADA
    return _to_response(
        solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.EN_PROGRESO)
    )

def rechazar(
    db: Session,
    id_solicitud: int,
    id_plomero: int
):

    solicitud = solicitud_repository.obtener_por_id(
        db,
        id_solicitud
    )

    if not solicitud:
        raise HTTPException(
            status_code=404,
            detail="No encontrada"
        )

    if solicitud.id_plomero != id_plomero:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )

    if solicitud.estado != EstadoSolicitud.EN_PROGRESO:
        raise HTTPException(
            status_code=400,
            detail="La solicitud no está en progreso"
        )

    # liberar plomero
    solicitud_repository.asignar_plomero(
        db,
        id_solicitud,
        None
    )

    # volver disponible
    solicitud = solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.PENDIENTE
    )

    return _to_response(solicitud)

def completar(db: Session, id_solicitud: int, id_plomero: int):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")
    if solicitud.estado != EstadoSolicitud.EN_PROGRESO:
        raise HTTPException(status_code=400, detail="No está en progreso")
    return _to_response(
        solicitud_repository.cambiar_estado(
            db, id_solicitud, EstadoSolicitud.PENDIENTE_CALIFICACION
        )
    )

def cancelar(db: Session, id_solicitud: int, id_usuario: int):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="Sin acceso")
    if solicitud.estado == EstadoSolicitud.EN_PROGRESO:
        raise HTTPException(status_code=400, detail="No se puede cancelar un trabajo en progreso")
    solicitud_repository.asignar_plomero(db, id_solicitud, None)
    return _to_response(
        solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.CANCELADA)
    )
# ─────────────────────────────────────────────
# BUSCAR
# ─────────────────────────────────────────────

def buscar_por_texto(db: Session, q: str):
    return solicitud_repository.buscar_por_texto(db, q)