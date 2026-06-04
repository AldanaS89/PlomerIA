import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from models.solicitud_plomero import EstadoInvitacion
from repositories import solicitud_plomero_repository
from services.notificacion_service import notificacion_service
from services import ia_service
from models.solicitud import EstadoSolicitud
from models.bloqueHorario import BloqueHorario
from schemas.solicitud import SolicitudCreate, SolicitudResponse

from repositories import (
    solicitud_repository,
    usuario_repository,
    plomero_repository,
)

from services.filtrado_service import filtrado_service
from services import calificacion_service as _cal_service

logger = logging.getLogger(__name__)


# ─── PENALIZACIONES ───────────────────────────────────────────────────────────
# La lógica completa de penalización (tiempo + comunicación) vive en
# calificacion_service.calcular_penalizacion() para mantener responsabilidad única.
# Este service solo delega a través de penalizar_por_cancelacion().

CANCELACIONES_PARA_SUSPENSION = 3
MAX_RONDAS_BUSQUEDA = 3

def _resetear_cancelaciones_plomero(db: Session, id_plomero: int):
    p = plomero_repository.buscar_por_id(db, id_plomero)
    if p:
        _cal_service.resetear_cancelaciones(db, p)


# ─────────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────────
def _to_response(s):

    estado = (
        s.estado.value
        if hasattr(s.estado, "value")
        else str(s.estado)
    )

    response = {
        "id_solicitud": s.id_solicitud,
        "id_usuario": s.id_usuario,
        "id_plomero": s.id_plomero,

        "descripcion_raw": s.descripcion_raw,
        "estado": estado,

        "fecha": (
            s.fecha.isoformat()
            if s.fecha
            else None
        ),

        "localidad_evento": s.localidad_evento,
        "latitud_evento": s.latitud_evento,
        "longitud_evento": s.longitud_evento,

        "etiqueta_ia": s.etiqueta_ia,
        "urgencia_ia": s.urgencia_ia,

        "fecha_trabajo": (
            s.fecha_trabajo.isoformat()
            if s.fecha_trabajo
            else None
        ),

        "presupuesto_min": s.presupuesto_min,
        "presupuesto_max": s.presupuesto_max,

        "nombre_cliente": None,
        "direccion_cliente": None,

        "nombre_plomero": None,
        "foto_plomero": None,
        "localidad_plomero": None,

        "invitaciones": [],
    }

    if s.usuario:
        response["nombre_cliente"] = (
            f"{s.usuario.nombre} {s.usuario.apellido}"
        )

    if s.plomero:
        response["nombre_plomero"] = (
            f"{s.plomero.nombre} {s.plomero.apellido}"
        )
        response["foto_plomero"] = s.plomero.foto_perfil_path
        response["localidad_plomero"] = s.plomero.localidad

    if estado in {
        "en_progreso",
        "en_camino",
        "pendiente_calificacion",
        "completada",
    }:
        if s.usuario:
            response["direccion_cliente"] = s.usuario.direccion

    for inv in s.plomeros:
        response["invitaciones"].append({
            "id_plomero": inv.id_plomero,
            "nombre": (
                f"{inv.plomero.nombre} {inv.plomero.apellido}"
                if inv.plomero else None
            ),
            "estado": inv.estado.value,
            "fecha": (
                inv.fecha.isoformat()
                if inv.fecha
                else None
            )
        })

    return response

def _marcar_bloque_ocupado(db, id_plomero, fecha_trabajo):
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
        logger.warning(f"No se pudo marcar bloque horario: {e}")

#Funcion interna para buscar 5 nuevos plomeros
def buscar_nuevos_plomeros(
    db: Session,
    solicitud
):
    solicitud.intentos_reasignacion += 1
    db.commit()

    if solicitud.intentos_reasignacion > MAX_RONDAS_BUSQUEDA:

        solicitud_repository.cambiar_estado(
            db,
            solicitud.id_solicitud,
            EstadoSolicitud.SIN_RESPUESTA
        )

        return {
            "ok": False,
            "mensaje": (
                "No se encontraron más profesionales "
                "disponibles."
            )
        }

    invitaciones = (
        solicitud_plomero_repository
        .obtener_invitaciones_por_solicitud(
            db,
            solicitud.id_solicitud
        )
    )

    excluidos = {
        inv.id_plomero
        for inv in invitaciones
    }

    candidatos = (
        plomero_repository.buscar_para_solicitud(
            db,
            especialidades=solicitud.etiqueta_ia,
            lat_usuario=solicitud.latitud_evento,
            lon_usuario=solicitud.longitud_evento,
            atiende_urgencias=(
                solicitud.urgencia_ia == "URGENTE"
            ),
            limite=50,
        )
    )

    nuevos = [
        p
        for p in candidatos
        if p.id_plomero not in excluidos
    ][:5]

    if not nuevos:

        solicitud_repository.cambiar_estado(
            db,
            solicitud.id_solicitud,
            EstadoSolicitud.SIN_RESPUESTA
        )

        return {
            "ok": False,
            "mensaje": (
                "No se encontraron más profesionales."
            )
        }

    solicitud_plomero_repository.crear_invitaciones_bulk(
        db,
        solicitud.id_solicitud,
        [p.id_plomero for p in nuevos]
    )

    notificacion_service.notificar_plomeros(
        plomeros=nuevos,
        solicitud_id=solicitud.id_solicitud,
        descripcion=solicitud.descripcion_raw,
        diagnostico={
            "etiqueta_ia": solicitud.etiqueta_ia,
            "urgencia_ia": solicitud.urgencia_ia,
            "presupuesto_min": solicitud.presupuesto_min,
            "presupuesto_max": solicitud.presupuesto_max,
        },
    )

    solicitud_repository.cambiar_estado(
        db,
        solicitud.id_solicitud,
        EstadoSolicitud.PENDIENTE
    )

    return {
        "ok": True,
        "mensaje": (
            f"Se notificó a {len(nuevos)} "
            f"nuevos plomeros."
        )
    }


# ─────────────────────────────────────────────
# CREAR SOLICITUD
# ─────────────────────────────────────────────
def crear_solicitud(
    db: Session,
    datos: SolicitudCreate,
    id_usuario: int
):
    diagnostico = ia_service.analizar_descripcion(
        datos.descripcion_raw
    )

    usuario = usuario_repository.buscar_por_id(
        db,
        id_usuario
    )

    if usuario and getattr(usuario, "suspendido", False):
        raise HTTPException(
            status_code=403,
            detail="Cuenta suspendida"
        )

    solicitud = solicitud_repository.crear(
        db,
        id_usuario,
        datos,
        diagnostico
    )

    ids_plomeros = datos.ids_plomeros_seleccionados or []

    plomeros = []

    for pid in ids_plomeros:
        plomero = plomero_repository.buscar_por_id(
            db,
            pid
        )

        if plomero:
            plomeros.append(plomero)

    solicitud_plomero_repository.crear_invitaciones_bulk(
        db,
        solicitud.id_solicitud,
        ids_plomeros
    )

    notificacion_service.notificar_plomeros(
        plomeros=plomeros,
        solicitud_id=solicitud.id_solicitud,
        descripcion=datos.descripcion_raw,
        diagnostico=diagnostico,
    )

    return _to_response(
        solicitud_repository.obtener_por_id(
            db,
            solicitud.id_solicitud
        )
    )
# ─────────────────────────────────────────────
# ACEPTAR
# ─────────────────────────────────────────────
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

    if solicitud.estado != EstadoSolicitud.PENDIENTE:
        raise HTTPException(
            status_code=400,
            detail="La solicitud ya no está disponible"
        )

    invitacion = solicitud_plomero_repository.obtener_invitacion(
        db,
        id_solicitud,
        id_plomero
    )

    if not invitacion:
        raise HTTPException(
            status_code=403,
            detail="No fuiste invitado a esta solicitud"
        )

    if invitacion.estado != EstadoInvitacion.CONTACTADO:
        raise HTTPException(
            status_code=400,
            detail="La invitación ya no está disponible"
        )

    # Asignar ganador
    solicitud_repository.asignar_plomero(
        db,
        id_solicitud,
        id_plomero
    )

    # Invitación aceptada
    solicitud_plomero_repository.cambiar_estado_invitacion(
        db,
        id_solicitud,
        id_plomero,
        EstadoInvitacion.ACEPTADO
    )

    # Cancelar el resto
    invitaciones = (
        solicitud_plomero_repository.obtener_por_solicitud(
            db,
            id_solicitud
        )
    )

    for inv in invitaciones:

        if inv.id_plomero == id_plomero:
            continue

        if inv.estado == EstadoInvitacion.CONTACTADO:

            solicitud_plomero_repository.cambiar_estado_invitacion(
                db,
                id_solicitud,
                inv.id_plomero,
                EstadoInvitacion.CANCELADO
            )

    # Solicitud en progreso
    solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.EN_PROGRESO
    )

    _marcar_bloque_ocupado(
        db,
        id_plomero,
        solicitud.fecha_trabajo
    )

    _resetear_cancelaciones_plomero(
        db,
        id_plomero
    )

    solicitud = solicitud_repository.obtener_por_id(
        db,
        id_solicitud
    )

    return _to_response(solicitud)
# ─────────────────────────────────────────────
# RECHAZAR
# ─────────────────────────────────────────────
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
            detail="Solicitud no encontrada"
        )

    invitacion = (
        solicitud_plomero_repository.obtener_invitacion(
            db,
            id_solicitud,
            id_plomero
        )
    )

    if not invitacion:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )

    if invitacion.estado != EstadoInvitacion.CONTACTADO:
        raise HTTPException(
            status_code=400,
            detail="La invitación ya fue respondida"
        )

    # marcar rechazo
    solicitud_plomero_repository.cambiar_estado_invitacion(
        db,
        id_solicitud,
        id_plomero,
        EstadoInvitacion.RECHAZADO
    )

    # ¿queda alguien sin responder?
    activos = solicitud_plomero_repository.obtener_activos(
        db,
        id_solicitud
    )

    if activos:
        return {
            "mensaje": "Invitación rechazada"
        }

    # ya nadie puede aceptar
    if solicitud.intentos_reasignacion >= MAX_RONDAS_BUSQUEDA:

        solicitud_repository.cambiar_estado(
            db,
            id_solicitud,
            EstadoSolicitud.SIN_RESPUESTA
        )

        return {
            "mensaje": "No hay más plomeros disponibles"
        }

    # todos los plomeros que ya participaron
    invitaciones = (
        solicitud_plomero_repository
        .obtener_invitaciones_por_solicitud(
            db,
            id_solicitud
        )
    )

    ids_excluidos = {
        inv.id_plomero
        for inv in invitaciones
    }

    candidatos = (
        plomero_repository.buscar_para_solicitud(
            db,
            especialidades=solicitud.etiqueta_ia,
            lat_usuario=solicitud.latitud_evento,
            lon_usuario=solicitud.longitud_evento,
            atiende_urgencias=(
                solicitud.urgencia_ia == "URGENTE"
            ),
            limite=50,
        )
    )

    nuevos = [
        p
        for p in candidatos
        if p.id_plomero not in ids_excluidos
    ][:5]

    if not nuevos:

        solicitud_repository.cambiar_estado(
            db,
            id_solicitud,
            EstadoSolicitud.SIN_RESPUESTA
        )

        return {
            "mensaje": "No hay más plomeros disponibles"
        }

    solicitud_plomero_repository.crear_invitaciones_bulk(
        db,
        id_solicitud,
        [p.id_plomero for p in nuevos]
    )

    solicitud.intentos_reasignacion += 1
    db.commit()

    notificacion_service.notificar_plomeros(
        plomeros=nuevos,
        solicitud_id=id_solicitud,
        descripcion=solicitud.descripcion_raw,
        diagnostico={
            "etiqueta_ia": solicitud.etiqueta_ia,
            "urgencia_ia": solicitud.urgencia_ia,
            "presupuesto_min": solicitud.presupuesto_min,
            "presupuesto_max": solicitud.presupuesto_max,
        },
    )

    return {
        "mensaje": f"Se enviaron {len(nuevos)} nuevas invitaciones"
    }
# ─────────────────────────────────────────────
# EN CAMINO
# ─────────────────────────────────────────────

def marcar_en_camino(
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

    if (
        solicitud.fecha_trabajo
        and solicitud.fecha_trabajo.date()
        != datetime.now().date()
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Solo podés marcar EN CAMINO "
                "el día del trabajo"
            )
        )

    solicitud = solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.EN_CAMINO
    )

    return _to_response(solicitud)
# ─────────────────────────────────────────────
# COMPLETAR
# ─────────────────────────────────────────────

def completar(
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

    if solicitud.estado != EstadoSolicitud.EN_CAMINO:
        raise HTTPException(
            status_code=400,
            detail=(
                "Solo podés completar "
                "un trabajo EN CAMINO"
            )
        )

    _resetear_cancelaciones_plomero(
        db,
        id_plomero
    )

    solicitud = solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.PENDIENTE_CALIFICACION
    )

    return _to_response(solicitud)

def cancelar(db: Session, id_solicitud: int, id_usuario: int):
    """
    Cancelacion por parte del CLIENTE.
    - Sin plomero asignado → sin penalizacion, cierra la solicitud.
    - Con plomero asignado → penalizacion al cliente, cierra la solicitud.
    - En REASIGNACION_PENDIENTE (el plomero ya cancelo) → sin penalizacion.
    """
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="Sin acceso")
    if solicitud.estado == EstadoSolicitud.EN_CAMINO:
        raise HTTPException(
            status_code=400,
            detail="No se puede cancelar — el profesional ya esta en camino"
        )

    estados_cancelables = (
        EstadoSolicitud.PENDIENTE,
        EstadoSolicitud.EN_PROGRESO,
        EstadoSolicitud.REASIGNACION_PENDIENTE,
    )
    if solicitud.estado not in estados_cancelables:
        raise HTTPException(
            status_code=400,
            detail="No se puede cancelar en este estado"
        )

    # Penalizar solo si habia plomero asignado y el cliente cancela directamente
    habia_plomero   = solicitud.id_plomero is not None
    en_reasignacion = solicitud.estado == EstadoSolicitud.REASIGNACION_PENDIENTE

    penalizacion = 0.0
    if habia_plomero and not en_reasignacion:
        penalizacion = _cal_service.penalizar_por_cancelacion(
            db, solicitud, id_usuario, "cliente"
        )

    solicitud_repository.asignar_plomero(db, id_solicitud, None)
    s = solicitud_repository.cambiar_estado(
        db, id_solicitud, EstadoSolicitud.CANCELADA
    )

    return {
        **_to_response(s),
        "penalizacion_aplicada": penalizacion,
        "mensaje": (
            "Solicitud cancelada sin penalizacion"
            if penalizacion == 0
            else f"Solicitud cancelada — calificacion automatica de {penalizacion} estrellas aplicada a tu promedio"
        ),
    }


def cancelar_plomero(
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

    if solicitud.estado not in (
        EstadoSolicitud.EN_PROGRESO,
        EstadoSolicitud.EN_CAMINO,
    ):
        raise HTTPException(
            status_code=400,
            detail="No se puede cancelar en este estado"
        )

    # Penalización automática
    penalizacion = _cal_service.penalizar_por_cancelacion(
        db,
        solicitud,
        id_plomero,
        "plomero"
    )

    # Marcar invitación
    solicitud_plomero_repository.cambiar_estado_invitacion(
        db,
        id_solicitud,
        id_plomero,
        EstadoInvitacion.CANCELADO
    )

    # Liberar plomero asignado
    solicitud_repository.asignar_plomero(
        db,
        id_solicitud,
        None
    )

    # Queda esperando decisión del cliente
    solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.REASIGNACION_PENDIENTE
    )

    solicitud_actualizada = solicitud_repository.obtener_por_id(
        db,
        id_solicitud
    )

    return {
        "solicitud": _to_response(
            solicitud_actualizada
        ),
        "penalizacion_plomero": penalizacion,
        "mensaje": (
            "El profesional canceló el trabajo. "
            "Podés buscar nuevos plomeros sin volver a crear la solicitud."
        )
    }

# ─────────────────────────────────────────────
# LISTADOS
# ─────────────────────────────────────────────

def listar_por_usuario(db: Session, id_usuario: int):
    return [_to_response(s) for s in solicitud_repository.listar_por_usuario(db, id_usuario)]


def listar_por_plomero(db: Session, id_plomero: int):
    return [_to_response(s) for s in solicitud_repository.listar_por_plomero(db, id_plomero)]


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
# BUSCAR
# ─────────────────────────────────────────────

def buscar_por_texto(db: Session, q: str):
    return solicitud_repository.buscar_por_texto(db, q)