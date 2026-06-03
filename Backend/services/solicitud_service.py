import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from services.notificacion_service import notificacion_service
from services import ia_service
from models.solicitud import EstadoSolicitud
from models.bloqueHorario import BloqueHorario
from schemas.solicitud import SolicitudCreate

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


def _resetear_cancelaciones_plomero(db: Session, id_plomero: int):
    p = plomero_repository.buscar_por_id(db, id_plomero)
    if p:
        _cal_service.resetear_cancelaciones(db, p)


# ─────────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────────

def _to_response(s) -> dict:
    """Serializa una solicitud enriquecida con datos del plomero y cliente."""

    estado_val = s.estado.value if hasattr(s.estado, "value") else str(s.estado)

    result = {
        "id_solicitud": s.id_solicitud,
        "id_usuario": s.id_usuario,
        "id_plomero": s.id_plomero,

        "descripcion_raw": s.descripcion_raw,
        "estado": estado_val,
        "fecha": s.fecha.isoformat() if s.fecha else None,

        "localidad_evento": s.localidad_evento,
        "latitud_evento": s.latitud_evento,
        "longitud_evento": s.longitud_evento,

        "etiqueta_ia": s.etiqueta_ia,
        "urgencia_ia": s.urgencia_ia,
        "turno_solicitado": s.turno_solicitado,

        "fecha_trabajo": (
            s.fecha_trabajo.isoformat() if s.fecha_trabajo else None
        ),

        "presupuesto_min": s.presupuesto_min,
        "presupuesto_max": s.presupuesto_max,

        # tracking marketplace
        "ids_plomeros_sugeridos": s.ids_plomeros_sugeridos,
        "ids_plomeros_contactados": s.ids_plomeros_contactados,
        "ids_plomeros_activos": s.ids_plomeros_activos,

        # plomero asignado
        "nombre_plomero": None,
        "foto_plomero": None,
        "localidad_plomero": None,

        # cliente
        "nombre_cliente": None,
        "direccion_cliente": None,

        # sugeridos enriquecidos (si los usás en front)
        "plomeros_sugeridos_detallados": [],
    }

    # ─── plomero asignado ─────────────────────────────
    if s.plomero:
        result["nombre_plomero"] = f"{s.plomero.nombre} {s.plomero.apellido}"
        result["foto_plomero"] = s.plomero.foto_perfil_path
        result["localidad_plomero"] = s.plomero.localidad

    # ─── cliente ─────────────────────────────
    if s.usuario:
        result["nombre_cliente"] = f"{s.usuario.nombre} {s.usuario.apellido}"

    # ─── dirección (solo estados activos) ─────────────────────────────
    ESTADOS_CON_DIRECCION = {
        "en_progreso",
        "en_camino",
        "pendiente_calificacion",
        "completada",
    }

    if estado_val in ESTADOS_CON_DIRECCION and s.usuario:
        result["direccion_cliente"] = s.usuario.direccion

    return result


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


# ─────────────────────────────────────────────
# CREAR SOLICITUD
# ─────────────────────────────────────────────

def crear_solicitud(db: Session, datos: SolicitudCreate, id_usuario: int):

    diagnostico = ia_service.analizar_descripcion(datos.descripcion_raw)

    usuario = usuario_repository.buscar_por_id(db, id_usuario)

    # Verificar si el cliente está suspendido
    if usuario and getattr(usuario, "suspendido", False):
        raise HTTPException(
            status_code=403,
            detail="Tu cuenta está suspendida por cancelaciones reiteradas. Contactá a soporte."
        )

    lat = datos.latitud_evento or (usuario.latitud if usuario else None)
    lon = datos.longitud_evento or (usuario.longitud if usuario else None)

    es_urgente = diagnostico["urgencia_ia"] == "URGENTE"
    ids_seleccionados  = datos.ids_plomeros_seleccionados or []
    turnos_por_plomero = datos.turnos_por_plomero or {}

    if ids_seleccionados:
        plomero = None
        turno_elegido = None
        for pid in ids_seleccionados:
            p = plomero_repository.buscar_por_id(db, pid)
            if p and p.disponible_ahora:
                plomero = p
                turno_elegido = turnos_por_plomero.get(str(pid))
                break
        if not plomero and ids_seleccionados:
            plomero = plomero_repository.buscar_por_id(db, ids_seleccionados[0])
            turno_elegido = turnos_por_plomero.get(str(ids_seleccionados[0]))
    else:
        plomeros = filtrado_service.obtener_plomeros_para_solicitud(
            db=db, etiqueta=diagnostico["etiqueta_ia"],
            lat=lat, lon=lon, es_urgente=es_urgente,
        )
        plomero = plomeros[0] if plomeros else None
        turno_elegido = None

    ids_str = ",".join(str(i) for i in ids_seleccionados) if ids_seleccionados else None

    # Crear solicitud incluyendo turno_solicitado desde el principio
    # para garantizar que se persista en el mismo commit
    solicitud = solicitud_repository.crear(
        db, id_usuario, datos, diagnostico,
        turno_solicitado=turno_elegido,
        ids_plomeros_sugeridos=ids_str,
        id_plomero=plomero.id_plomero if plomero else None,
    )

    db.refresh(solicitud)
    return _to_response(solicitud)


# ─────────────────────────────────────────────
# ACEPTAR
# ─────────────────────────────────────────────

def aceptar(db: Session, id_solicitud: int, id_plomero: int):

    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")

    logger.debug(
        "Aceptar solicitud %s — plomero %s — estado actual: %s",
        id_solicitud, id_plomero, solicitud.estado
    )

    if solicitud.estado not in (
        EstadoSolicitud.PENDIENTE,
        EstadoSolicitud.REASIGNACION_PENDIENTE,
    ):
        raise HTTPException(status_code=400, detail="La solicitud ya no está disponible")

    if solicitud.id_plomero:
        raise HTTPException(status_code=400, detail="La solicitud ya tiene un plomero asignado")

    # Validar que esté dentro de los sugeridos
    sugeridos = set(filter(None, (solicitud.ids_plomeros_sugeridos or "").split(",")))

    if sugeridos and str(id_plomero) not in sugeridos:
        raise HTTPException(
            status_code=403,
            detail="El plomero seleccionado no pertenece a esta solicitud"
        )

    solicitud_repository.asignar_plomero(db, id_solicitud, id_plomero)
    _marcar_bloque_ocupado(db, id_plomero, solicitud.fecha_trabajo)
    _resetear_cancelaciones_plomero(db, id_plomero)

    s = solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.EN_PROGRESO)

    logger.debug("Solicitud %s asignada al plomero %s", id_solicitud, id_plomero)

    return _to_response(s)


# ─────────────────────────────────────────────
# EN CAMINO
# ─────────────────────────────────────────────

def marcar_en_camino(db: Session, id_solicitud: int, id_plomero: int):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")

    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")

    if solicitud.estado != EstadoSolicitud.EN_PROGRESO:
        raise HTTPException(status_code=400, detail="No está en progreso")

    # Solo puede marcar EN CAMINO el día del trabajo
    if solicitud.fecha_trabajo:
        if solicitud.fecha_trabajo.date() != datetime.now().date():
            raise HTTPException(
                status_code=400,
                detail="Solo podés marcar EN CAMINO el día del trabajo"
            )

    s = solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.EN_CAMINO)
    return _to_response(s)


# ─────────────────────────────────────────────
# COMPLETAR — plomero marca que terminó el trabajo
# ─────────────────────────────────────────────

def completar(db: Session, id_solicitud: int, id_plomero: int):
    """
    El plomero marca el trabajo como terminado.
    La solicitud pasa a PENDIENTE_CALIFICACION para que el cliente pueda calificar.
    Solo disponible cuando el estado es EN_CAMINO.
    """
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")

    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")

    if solicitud.estado != EstadoSolicitud.EN_CAMINO:
        raise HTTPException(
            status_code=400,
            detail="Solo podés marcar como terminado cuando estás en camino"
        )

    # Resetear cancelaciones consecutivas al completar exitosamente
    _resetear_cancelaciones_plomero(db, id_plomero)

    s = solicitud_repository.cambiar_estado(
        db, id_solicitud, EstadoSolicitud.PENDIENTE_CALIFICACION
    )
    return _to_response(s)


# ─────────────────────────────────────────────
# RECHAZO (PLOMERO RECHAZA — CLIENTE VUELVE A ELEGIR)
# ─────────────────────────────────────────────

def rechazar(db: Session, id_solicitud: int, id_plomero: int):
    s = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not s:
        raise HTTPException(status_code=404, detail="No encontrada")

    if s.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")

    # Registrar como contactado (para no volver a sugerirlo)
    solicitud_repository.agregar_contactado(db, id_solicitud, id_plomero)

    # Desasignar plomero actual
    solicitud_repository.asignar_plomero(db, id_solicitud, None)

    # Obtener plomeros ya contactados
    contactados = solicitud_repository.obtener_contactados(db, id_solicitud)

    # Buscar candidatos compatibles excluyendo contactados
    candidatos = plomero_repository.buscar_para_solicitud(
        db,
        especialidades=s.etiqueta_ia,
        lat_usuario=s.latitud_evento,
        lon_usuario=s.longitud_evento,
        atiende_urgencias=(s.urgencia_ia == "URGENTE"),
        limite=50,
    )

    opciones = [p for p in candidatos if str(p.id_plomero) not in contactados][:5]

    if opciones:
        solicitud_repository.guardar_ids_sugeridos(db, id_solicitud, [p.id_plomero for p in opciones])
        solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.PENDIENTE)
        mensaje = f"Se encontraron {len(opciones)} nuevos plomeros para elegir."
    else:
        solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.REASIGNACION_PENDIENTE)
        mensaje = "No hay más plomeros disponibles por ahora."

    s = solicitud_repository.obtener_por_id(db, id_solicitud)
    return {
        "solicitud": _to_response(s),
        "opciones": [
            {
                "id_plomero": p.id_plomero,
                "nombre": f"{p.nombre} {p.apellido}",
                "localidad": p.localidad,
                "puntuacion": p.puntuacion,
            }
            for p in opciones
        ],
        "mensaje": mensaje,
    }


# ─────────────────────────────────────────────
# CANCELAR
# ─────────────────────────────────────────────
#
# Tres situaciones con consecuencias distintas:
#
# 1. Cliente cancela SIN plomero asignado (nadie respondio)
#    → Sin penalizacion. Solicitud a CANCELADA.
#
# 2. Cliente cancela CON plomero ya asignado
#    → Penalizacion al cliente (calificacion automatica al promedio).
#    → Solicitud a CANCELADA.
#
# 3. Plomero cancela despues de haber aceptado
#    → Penalizacion al plomero (calificacion automatica al promedio).
#    → Solicitud a REASIGNACION_PENDIENTE si quedan intentos (max 3).
#    → Solicitud a CANCELADA si se agotaron los intentos.
#    → Si el cliente decide no seguir buscando: sin penalizacion para el.

MAX_INTENTOS_REASIGNACION = 3


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


def cancelar_plomero(db: Session, id_solicitud: int, id_plomero: int):
    """
    Cancelacion por parte del PLOMERO despues de haber aceptado.
    - Siempre penaliza al plomero con calificacion automatica.
    - Si quedan intentos → REASIGNACION_PENDIENTE (solicitud sigue activa).
    - Si se agotaron los 3 intentos → CANCELADA.
    """
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")

    estados_cancelables = (
        EstadoSolicitud.EN_PROGRESO,
        EstadoSolicitud.EN_CAMINO,
    )
    if solicitud.estado not in estados_cancelables:
        raise HTTPException(
            status_code=400,
            detail="No se puede cancelar en este estado"
        )

    # Penalizar al plomero siempre
    penalizacion = _cal_service.penalizar_por_cancelacion(
        db, solicitud, id_plomero, "plomero"
    )

    # Registrar como contactado para no sugerirlo de nuevo
    solicitud_repository.agregar_contactado(db, id_solicitud, id_plomero)

    # Desasignar plomero
    solicitud_repository.asignar_plomero(db, id_solicitud, None)

    # Verificar intentos restantes
    intentos_usados = solicitud.intentos_reasignacion or 0

    if intentos_usados < MAX_INTENTOS_REASIGNACION:
        # Solicitud sigue activa, incrementar contador
        solicitud_repository.actualizar_activos(db, id_solicitud, [])
        s = solicitud_repository.cambiar_estado(
            db, id_solicitud, EstadoSolicitud.REASIGNACION_PENDIENTE
        )
        # Incrementar manualmente el contador de intentos
        sol = solicitud_repository.obtener_por_id(db, id_solicitud)
        if sol:
            sol.intentos_reasignacion = intentos_usados + 1
            db.commit()

        intentos_restantes = MAX_INTENTOS_REASIGNACION - (intentos_usados + 1)
        mensaje = (
            f"El trabajo fue cancelado por el profesional. "
            f"Podes volver a buscar ({intentos_restantes} intento{'s' if intentos_restantes != 1 else ''} restante{'s' if intentos_restantes != 1 else ''})."
        )
    else:
        # Sin mas intentos, cerrar
        s = solicitud_repository.cambiar_estado(
            db, id_solicitud, EstadoSolicitud.CANCELADA
        )
        mensaje = (
            "El trabajo fue cancelado por el profesional. "
            "Se agotaron los intentos de reasignacion."
        )

    return {
        **_to_response(s),
        "penalizacion_plomero": penalizacion,
        "intentos_usados": intentos_usados + 1,
        "mensaje": mensaje,
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