# services/solicitud_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from schemas.solicitud import SolicitudCreate, SolicitudResponse
from models.solicitud import EstadoSolicitud

from repositories import (
    solicitud_repository,
    usuario_repository
)

from services.ia_service import analizar_descripcion
from services.notificacion_service import notificacion_service
from services.filtrado_service import filtrado_service


def _to_response(s) -> SolicitudResponse:
    return SolicitudResponse.model_validate(s)


# ─────────────────────────────────────────────────────────────
# CREAR SOLICITUD
# ─────────────────────────────────────────────────────────────

def crear_solicitud(
    db: Session,
    datos: SolicitudCreate,
    id_usuario: int
) -> dict:

    # 1 — IA
    diagnostico = analizar_descripcion(
        datos.descripcion_raw
    )

    es_urgente = (
        diagnostico["urgencia_ia"] == "URGENTE"
    )

    # 2 — Crear solicitud
    solicitud = solicitud_repository.crear(
        db,
        id_usuario,
        datos,
        diagnostico
    )

    # 3 — Buscar ubicación usuario
    usuario = usuario_repository.buscar_por_id(
        db,
        id_usuario
    )

    lat = usuario.latitud if usuario else None
    lon = usuario.longitud if usuario else None

    # 4 — Filtrar plomeros
    plomeros = filtrado_service.obtener_plomeros_para_solicitud(
        db,
        etiqueta=diagnostico["etiqueta_ia"],
        lat=lat,
        lon=lon,
        es_urgente=es_urgente,
        ids_seleccionados=datos.ids_plomeros_seleccionados or [],
    )

    # 5 — Guardar IDs sugeridos
    if plomeros:
        solicitud_repository.guardar_ids_sugeridos(
            db,
            solicitud.id_solicitud,
            [p.id_plomero for p in plomeros]
        )

    # 6 — Notificar
    notificados = notificacion_service.notificar_plomeros(
        plomeros=plomeros,
        solicitud_id=solicitud.id_solicitud,
        descripcion=datos.descripcion_raw,
        diagnostico=diagnostico,
    )

    return {
        "id_solicitud": solicitud.id_solicitud,
        "etiqueta_ia": diagnostico["etiqueta_ia"],
        "urgencia_ia": diagnostico["urgencia_ia"],
        "presupuesto_min": diagnostico["presupuesto_min"],
        "presupuesto_max": diagnostico["presupuesto_max"],
        "explicacion": diagnostico.get("explicacion", ""),
        "plomeros_avisados": notificados,
        "estado": "pendiente",
    }


# ─────────────────────────────────────────────────────────────
# OBTENER
# ─────────────────────────────────────────────────────────────

def obtener_por_id_s(
    db: Session,
    id_solicitud: int
):
    solicitud = solicitud_repository.obtener_por_id(
        db,
        id_solicitud
    )

    if not solicitud:
        return None

    return _to_response(solicitud)


def obtener_para_usuario(
    db: Session,
    id_solicitud: int,
    id_usuario: int
):
    solicitud = solicitud_repository.obtener_por_id(
        db,
        id_solicitud
    )

    if not solicitud:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada"
        )

    if solicitud.id_usuario != id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No tenés acceso a esta solicitud"
        )

    return solicitud


# ─────────────────────────────────────────────────────────────
# LISTADOS
# ─────────────────────────────────────────────────────────────

def listar_por_usuario_s(
    db: Session,
    id_usuario: int
):
    solicitudes = solicitud_repository.listar_por_usuario(
        db,
        id_usuario
    )

    return [
        _to_response(s)
        for s in solicitudes
    ]


def listar_por_usuario_con_detalle_s(
    db: Session,
    id_usuario: int
):
    return solicitud_repository.listar_por_usuario_con_detalle(
        db,
        id_usuario
    )


def listar_por_plomero_s(
    db: Session,
    id_plomero: int
):
    solicitudes = solicitud_repository.listar_por_plomero(
        db,
        id_plomero
    )

    return [
        {
            "id_solicitud": s.id_solicitud,
            "id_usuario": s.id_usuario,
            "id_plomero": s.id_plomero,
            "descripcion_raw": s.descripcion_raw,
            "etiqueta_ia": s.etiqueta_ia,
            "urgencia_ia": s.urgencia_ia,
            "localidad_evento": s.localidad_evento,
            "estado": (
                s.estado.value
                if hasattr(s.estado, "value")
                else str(s.estado)
            ),
            "fecha": (
                s.fecha.isoformat()
                if s.fecha
                else None
            ),
        }
        for s in solicitudes
    ]


# ─────────────────────────────────────────────────────────────
# ESTADOS
# ─────────────────────────────────────────────────────────────

def _cambiar_estado_plomero(
    db: Session,
    id_solicitud: int,
    id_plomero: int,
    nuevo_estado: EstadoSolicitud,
):

    solicitud = solicitud_repository.obtener_por_id(
        db,
        id_solicitud
    )

    if not solicitud:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada"
        )

    if solicitud.id_plomero != id_plomero:
        raise HTTPException(
            status_code=403,
            detail="Esta solicitud no está asignada a vos"
        )

    solicitud = solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        nuevo_estado
    )

    return _to_response(solicitud)


def aceptar(
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
            detail="Solicitud no encontrada"
        )

    if (
        solicitud.estado == EstadoSolicitud.ACEPTADO
        and solicitud.id_plomero
    ):
        raise HTTPException(
            status_code=400,
            detail="Otro plomero ya tomó este trabajo"
        )

    solicitud_repository.asignar_plomero(
        db,
        id_solicitud,
        id_plomero
    )

    return _cambiar_estado_plomero(
        db,
        id_solicitud,
        id_plomero,
        EstadoSolicitud.ACEPTADO
    )


def rechazar(
    db: Session,
    id_solicitud: int,
    id_plomero: int
):
    return _cambiar_estado_plomero(
        db,
        id_solicitud,
        id_plomero,
        EstadoSolicitud.RECHAZADO
    )


def completar(
    db: Session,
    id_solicitud: int,
    id_plomero: int
):
    return _cambiar_estado_plomero(
        db,
        id_solicitud,
        id_plomero,
        EstadoSolicitud.COMPLETADO
    )


# ─────────────────────────────────────────────────────────────
# CANCELAR
# ─────────────────────────────────────────────────────────────

def cancelar_solicitud(
    db: Session,
    id_solicitud: int,
    id_usuario: int
):

    solicitud = solicitud_repository.obtener_por_id(
        db,
        id_solicitud
    )

    if not solicitud:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada"
        )

    if solicitud.id_usuario != id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No podés cancelar una solicitud que no es tuya"
        )

    if solicitud.estado == EstadoSolicitud.ACEPTADO:
        raise HTTPException(
            status_code=400,
            detail="No podés cancelar una solicitud ya aceptada"
        )

    solicitud_repository.cancelar(
        db,
        solicitud
    )

    return {
        "status": "ok",
        "mensaje": "Solicitud cancelada"
    }


# ─────────────────────────────────────────────────────────────
# BUSCAR
# ─────────────────────────────────────────────────────────────

def buscar_por_texto(
    db: Session,
    q: str
):
    return solicitud_repository.buscar_por_texto(
        db,
        q
    )