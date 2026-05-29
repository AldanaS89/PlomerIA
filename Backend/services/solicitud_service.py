# services/solicitud_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from models.solicitud import EstadoSolicitud
from models.bloqueHorario import BloqueHorario
from schemas.solicitud import SolicitudCreate

from repositories import (
    solicitud_repository,
    usuario_repository,
    plomero_repository,
)

from services import ia_service
from services.filtrado_service import filtrado_service


# ─── PENALIZACIONES ───────────────────────────────────────────────────────────
HORAS_SIN_PENALIZACION = 24   # más de 24hs antes → sin penalización
PENALIZACION_CON_AVISO = 0.5  # menos de 24hs → -0.5
PENALIZACION_MISMO_DIA = 1.0  # mismo día → -1.0
CANCELACIONES_PARA_SUSPENSION = 3


def _calcular_penalizacion(turno_str: str | None) -> float:
    """Calcula la penalización según cuánto tiempo falta para el turno."""
    if not turno_str:
        return PENALIZACION_CON_AVISO

    try:
        # turno_str: "Lun_manana_9" → intentar parsear
        partes = turno_str.split("_")
        if len(partes) < 3:
            return PENALIZACION_CON_AVISO

        dia_str  = partes[0]
        hora_str = partes[2] if len(partes) > 2 else "9"
        hora     = int(hora_str)

        IDX = {"Lun":0,"Mar":1,"Mié":2,"Jue":3,"Vie":4,"Sáb":5,"Dom":6}
        dia_idx = IDX.get(dia_str, 0)

        hoy     = datetime.now()
        diff    = (dia_idx - hoy.weekday()) % 7
        turno_dt = hoy.replace(hour=hora, minute=0, second=0, microsecond=0)
        turno_dt += timedelta(days=diff if diff > 0 else 7)

        horas_restantes = (turno_dt - hoy).total_seconds() / 3600

        if horas_restantes > HORAS_SIN_PENALIZACION:
            return 0.0
        elif horas_restantes > 0:
            # Mismo día (menos de 8hs)
            if horas_restantes < 8:
                return PENALIZACION_MISMO_DIA
            return PENALIZACION_CON_AVISO
        else:
            return PENALIZACION_MISMO_DIA
    except Exception:
        return PENALIZACION_CON_AVISO


def _aplicar_penalizacion_plomero(db: Session, id_plomero: int, penalizacion: float):
    """Resta puntuación y controla suspensión por cancelaciones consecutivas."""
    if penalizacion <= 0:
        return
    p = plomero_repository.buscar_por_id(db, id_plomero)
    if not p:
        return
    p.puntuacion = max(1.0, round(p.puntuacion - penalizacion, 1))
    p.cancelaciones_consecutivas = (p.cancelaciones_consecutivas or 0) + 1
    if p.cancelaciones_consecutivas >= CANCELACIONES_PARA_SUSPENSION:
        p.disponible_ahora = False
        p.suspendido = True
    db.commit()


def _aplicar_penalizacion_cliente(db: Session, id_usuario: int, penalizacion: float):
    """Registra cancelaciones del cliente y suspende si acumula 3 seguidas."""
    if penalizacion <= 0:
        return
    u = usuario_repository.buscar_por_id(db, id_usuario)
    if not u:
        return
    u.cancelaciones_consecutivas = (u.cancelaciones_consecutivas or 0) + 1
    if u.cancelaciones_consecutivas >= CANCELACIONES_PARA_SUSPENSION:
        u.suspendido = True
    db.commit()


def _resetear_cancelaciones_plomero(db: Session, id_plomero: int):
    p = plomero_repository.buscar_por_id(db, id_plomero)
    if p:
        p.cancelaciones_consecutivas = 0
        db.commit()


def _to_response(s) -> dict:
    """Serializa una solicitud enriquecida con datos del plomero y cliente."""
    estado_val = s.estado.value if hasattr(s.estado, "value") else str(s.estado)

    result = {
        "id_solicitud":          s.id_solicitud,
        "id_usuario":            s.id_usuario,
        "id_plomero":            s.id_plomero,
        "descripcion_raw":       s.descripcion_raw,
        "estado":                estado_val,
        "fecha":                 s.fecha.isoformat() if s.fecha else None,
        "localidad_evento":      s.localidad_evento,
        "latitud_evento":        s.latitud_evento,
        "longitud_evento":       s.longitud_evento,
        "etiqueta_ia":           s.etiqueta_ia,
        "urgencia_ia":           s.urgencia_ia,
        "turno_solicitado":      s.turno_solicitado,
        "presupuesto_min":       s.presupuesto_min,
        "presupuesto_max":       s.presupuesto_max,
        "ids_plomeros_sugeridos": s.ids_plomeros_sugeridos,
        # Datos del plomero asignado
        "nombre_plomero":        None,
        "foto_plomero":          None,
        "localidad_plomero":     None,
        # Dirección del cliente (solo visible cuando plomero aceptó)
        "direccion_cliente":     None,
        "plomeros_sugeridos_detallados": [],
    }

    # Enriquecer con datos del plomero si está asignado
    if s.plomero:
        result["nombre_plomero"]    = f"{s.plomero.nombre} {s.plomero.apellido}"
        result["foto_plomero"]      = s.plomero.foto_perfil_path
        result["localidad_plomero"] = s.plomero.localidad

    # Dirección del cliente — solo si el plomero ya aceptó
    ESTADOS_CON_DIRECCION = {
        "en_progreso", "en_camino",
        "pendiente_calificacion", "completada"
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
        print(f"[solicitud_service] No se pudo marcar bloque: {e}")


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

    solicitud = solicitud_repository.crear(db, id_usuario, datos, diagnostico)

    if ids_str:
        solicitud.ids_plomeros_sugeridos = ids_str
    if turno_elegido:
        solicitud.turno_solicitado = turno_elegido

    if plomero:
        solicitud.id_plomero = plomero.id_plomero
    solicitud.estado = EstadoSolicitud.PENDIENTE

    db.commit()
    db.refresh(solicitud)
    return _to_response(solicitud)


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
# ACEPTAR
# ─────────────────────────────────────────────

def aceptar(db: Session, id_solicitud: int, id_plomero: int):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.estado != EstadoSolicitud.PENDIENTE:
        raise HTTPException(status_code=400, detail="La solicitud ya no está disponible")

    solicitud_repository.asignar_plomero(db, id_solicitud, id_plomero)
    _marcar_bloque_ocupado(db, id_plomero, solicitud.fecha)
    _resetear_cancelaciones_plomero(db, id_plomero)

    s = solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.EN_PROGRESO)
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

    s = solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.EN_CAMINO)
    return _to_response(s)


# ─────────────────────────────────────────────
# RECHAZAR
# ─────────────────────────────────────────────

def rechazar(db: Session, id_solicitud: int, id_plomero: int):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")
    if solicitud.estado not in (EstadoSolicitud.PENDIENTE, EstadoSolicitud.EN_PROGRESO):
        raise HTTPException(status_code=400, detail="No se puede rechazar en este estado")

    solicitud_repository.asignar_plomero(db, id_solicitud, None)
    s = solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.PENDIENTE)
    return _to_response(s)


# ─────────────────────────────────────────────
# COMPLETAR
# ─────────────────────────────────────────────

def completar(db: Session, id_solicitud: int, id_plomero: int):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")
    if solicitud.estado not in (EstadoSolicitud.EN_PROGRESO, EstadoSolicitud.EN_CAMINO):
        raise HTTPException(status_code=400, detail="No está en progreso")

    s = solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.PENDIENTE_CALIFICACION)
    return _to_response(s)


# ─────────────────────────────────────────────
# CANCELAR — con penalizaciones
# ─────────────────────────────────────────────

def cancelar(db: Session, id_solicitud: int, id_usuario: int):
    """Cancelación por parte del CLIENTE."""
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="Sin acceso")
    if solicitud.estado == EstadoSolicitud.EN_CAMINO:
        raise HTTPException(status_code=400, detail="No se puede cancelar — el profesional ya está en camino")
    if solicitud.estado not in (EstadoSolicitud.PENDIENTE, EstadoSolicitud.EN_PROGRESO):
        raise HTTPException(status_code=400, detail="No se puede cancelar en este estado")

    penalizacion = _calcular_penalizacion(solicitud.turno_solicitado)
    _aplicar_penalizacion_cliente(db, id_usuario, penalizacion)

    solicitud_repository.asignar_plomero(db, id_solicitud, None)
    s = solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.CANCELADA)
    return {
        **_to_response(s),
        "penalizacion_aplicada": penalizacion,
        "mensaje": "Solicitud cancelada" + (f" — se aplicó una penalización de {penalizacion} puntos" if penalizacion > 0 else " sin penalización"),
    }


def cancelar_plomero(db: Session, id_solicitud: int, id_plomero: int):
    """Cancelación por parte del PLOMERO."""
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")
    if solicitud.estado not in (EstadoSolicitud.PENDIENTE, EstadoSolicitud.EN_PROGRESO):
        raise HTTPException(status_code=400, detail="No se puede cancelar en este estado")

    penalizacion = _calcular_penalizacion(solicitud.turno_solicitado)
    _aplicar_penalizacion_plomero(db, id_plomero, penalizacion)

    solicitud_repository.asignar_plomero(db, id_solicitud, None)
    s = solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.CANCELADA)
    return {
        **_to_response(s),
        "penalizacion_aplicada": penalizacion,
        "mensaje": "Trabajo cancelado" + (f" — se aplicó una penalización de {penalizacion} puntos" if penalizacion > 0 else " sin penalización"),
    }


# ─────────────────────────────────────────────
# BUSCAR
# ─────────────────────────────────────────────

def buscar_por_texto(db: Session, q: str):
    return solicitud_repository.buscar_por_texto(db, q)