# services/solicitud_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from schemas.solicitud import SolicitudCreate, SolicitudResponse
from models.solicitud import EstadoSolicitud
from repositories import solicitud_repository, plomero_repository, usuario_repository
from services import ia_service
from utils.email import enviar_solicitud_plomero

MAX_PLOMEROS = 5

def _to_response(s) -> SolicitudResponse:
    return SolicitudResponse.from_orm_obj(s)

def crear_solicitud(db: Session, datos: SolicitudCreate, id_usuario: int) -> dict:

    diagnostico = ia_service.analizar_descripcion(datos.descripcion_raw)
    es_urgente  = diagnostico["urgencia_ia"] == "URGENTE"

    solicitud = solicitud_repository.crear(db, id_usuario, datos, diagnostico)

    # ── Usar los IDs seleccionados por el cliente ─────────────────────────────
    ids_seleccionados = datos.ids_plomeros_seleccionados or []

    if ids_seleccionados:
        # El cliente eligió sus plomeros → usarlos directamente
        plomeros = [
            p for pid in ids_seleccionados
            if (p := plomero_repository.buscar_por_id(db, pid))
        ]
    else:
        # Fallback: calcular automáticamente (compatibilidad)
        usuario = usuario_repository.buscar_por_id(db, id_usuario)
        lat = usuario.latitud  if usuario else None
        lon = usuario.longitud if usuario else None

        plomeros = plomero_repository.buscar_para_solicitud(
            db,
            especialidades    = diagnostico["etiqueta_ia"],
            lat_usuario       = lat,
            lon_usuario       = lon,
            atiende_urgencias = es_urgente,
            limite            = 5,
        )
        if not plomeros:
            plomeros = plomero_repository.buscar_para_solicitud(
                db, lat_usuario=lat, lon_usuario=lon, limite=5
            )

    # Guardar exactamente los IDs notificados
    if plomeros:
        solicitud_repository.guardar_ids_sugeridos(
            db, solicitud.id_solicitud, [p.id_plomero for p in plomeros]
        )

    # Mandar email a cada plomero
    for plomero in plomeros:
        try:
            enviar_solicitud_plomero(
                plomero_email   = plomero.email,
                plomero_nombre  = plomero.nombre,
                solicitud_id    = solicitud.id_solicitud,
                descripcion     = datos.descripcion_raw,
                diagnostico     = diagnostico["etiqueta_ia"],
                urgencia        = diagnostico["urgencia_ia"],
                presupuesto_min = diagnostico["presupuesto_min"],
                presupuesto_max = diagnostico["presupuesto_max"],
            )
        except Exception as e:
            print(f"[solicitud_service] Error email {plomero.email}: {e}")

    return {
        "id_solicitud":      solicitud.id_solicitud,
        "etiqueta_ia":       diagnostico["etiqueta_ia"],
        "urgencia_ia":       diagnostico["urgencia_ia"],
        "presupuesto_min":   diagnostico["presupuesto_min"],
        "presupuesto_max":   diagnostico["presupuesto_max"],
        "explicacion":       diagnostico.get("explicacion", ""),
        "plomeros_avisados": len(plomeros),
        "estado":            "pendiente",
    }

def obtener_por_id_s(db: Session, id: int) -> SolicitudResponse | None:
    s = solicitud_repository.obtener_por_id(db, id)
    return _to_response(s) if s else None

def listar_por_usuario_s(db: Session, id_usuario: int) -> list[SolicitudResponse]:
    return [_to_response(s) for s in solicitud_repository.listar_por_usuario(db, id_usuario)]

def listar_por_plomero_s(db: Session, id_plomero: int) -> list[SolicitudResponse]:
    return [_to_response(s) for s in solicitud_repository.listar_por_plomero(db, id_plomero)]

def _cambiar_estado_plomero(
    db:           Session,
    id_solicitud: int,
    id_plomero:   int,
    nuevo_estado: EstadoSolicitud,
) -> SolicitudResponse:
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="Esta solicitud no está asignada a vos")
    solicitud = solicitud_repository.cambiar_estado(db, id_solicitud, nuevo_estado)
    return _to_response(solicitud)

def aceptar(db: Session, id_solicitud: int, id_plomero: int) -> SolicitudResponse:
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    # Primero asignar el plomero, después cambiar estado
    solicitud_repository.asignar_plomero(db, id_solicitud, id_plomero)
    return _cambiar_estado_plomero(db, id_solicitud, id_plomero, EstadoSolicitud.ACEPTADO)

def rechazar(db: Session, id_solicitud: int, id_plomero: int) -> SolicitudResponse:
    return _cambiar_estado_plomero(db, id_solicitud, id_plomero, EstadoSolicitud.RECHAZADO)

def completar(db: Session, id_solicitud: int, id_plomero: int) -> SolicitudResponse:
    return _cambiar_estado_plomero(db, id_solicitud, id_plomero, EstadoSolicitud.COMPLETADO)

def buscar_por_texto(db, q: str):
    from models.solicitud import Solicitud
    query = db.query(Solicitud)
    if q:
        query = query.filter(Solicitud.descripcion_raw.ilike(f"%{q}%"))
    return query.order_by(Solicitud.fecha.desc()).all()