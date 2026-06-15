import logging
import unicodedata

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from models.solicitud_plomero import EstadoInvitacion
from repositories import solicitud_plomero_repository
from services.notificacion_service import notificacion_service
from services import notificaciones_inapp
from services import ia_service
from services import moderacion
from models.solicitud import EstadoSolicitud, Solicitud
from models.bloqueHorario import BloqueHorario
from schemas.solicitud import SolicitudCreate, SolicitudResponse

from repositories import (
    solicitud_repository,
    usuario_repository,
    plomero_repository,
    calificacion_repository,
    material_repository,
    mensaje_repository,
)

from services.filtrado_service import filtrado_service
from services import calificacion_service as _cal_service

logger = logging.getLogger(__name__)


# Día de la semana en formato getDay() de JS: domingo=0 ... sábado=6
_DIAS_SEMANA = {
    "dom": 0, "lun": 1, "mar": 2, "mie": 3, "jue": 4, "vie": 5, "sab": 6,
}


def _calcular_fecha_trabajo(turno: str):
    """
    Convierte un turno tipo "Mié_manana_8" en la próxima fecha concreta
    (hoy o posterior) que cae en ese día de la semana, con esa hora.
    Devuelve None si el turno no es parseable.
    """
    if not turno:
        return None
    partes = turno.split("_")
    if len(partes) < 1:
        return None

    # Normalizar acentos: "Mié" -> "mie", "Sáb" -> "sab"
    dia_raw = partes[0].lower()
    dia = "".join(
        c for c in unicodedata.normalize("NFD", dia_raw)
        if unicodedata.category(c) != "Mn"
    )[:3]

    objetivo = _DIAS_SEMANA.get(dia)
    if objetivo is None:
        return None

    try:
        hora = int(partes[2]) if len(partes) >= 3 else 9
    except (ValueError, TypeError):
        hora = 9

    hoy = datetime.now()
    hoy_js = (hoy.weekday() + 1) % 7  # Python (lun=0) -> JS getDay (dom=0)
    delta = (objetivo - hoy_js) % 7   # 0 = hoy, si no, próximo día que coincide
    fecha = hoy + timedelta(days=delta)
    return fecha.replace(hour=hora, minute=0, second=0, microsecond=0)


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
        "diagnostico_ia": s.diagnostico_ia,

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
        "turno_solicitado": s.turno_solicitado,
        "intentos_reasignacion": s.intentos_reasignacion or 0,
        "intentos_restantes": max(0, MAX_RONDAS_BUSQUEDA - (s.intentos_reasignacion or 0)),
        # Cerrada automáticamente porque nadie aceptó tras agotar los reintentos.
        "cerrada_sin_respuesta": (
            estado == "cancelada"
            and s.id_plomero is None
            and (s.intentos_reasignacion or 0) >= MAX_RONDAS_BUSQUEDA
        ),
        # Trabajo en curso cuya fecha YA pasó y sigue sin cerrar (pendiente de cierre).
        "vencido_sin_cerrar": (
            estado in {"en_progreso", "en_camino"}
            and s.fecha_trabajo is not None
            and s.fecha_trabajo.date() < datetime.now().date()
        ),
        "fecha_ultimo_envio": (
            s.fecha_ultimo_envio.isoformat()
            if s.fecha_ultimo_envio
            else None
        ),
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

    # La dirección solo se muestra mientras el plomero necesita ir al domicilio.
    # Una vez que marca TERMINADO (→ pendiente_calificacion) ya llegó —
    # la dirección desaparece para proteger la privacidad del cliente.
    if estado in {
        "en_progreso",
        "en_camino",
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

    if moderacion.esta_suspendido(db, usuario):
        raise HTTPException(
            status_code=403,
            detail=moderacion.mensaje_suspension(usuario),
        )
    ids_plomeros = (
        datos.ids_plomeros_seleccionados or []
    )

    turno_elegido = None

    if ids_plomeros:
        turno_elegido = (
            datos.turnos_por_plomero.get(
                str(ids_plomeros[0])
            )
        )

    solicitud = solicitud_repository.crear(
        db,
        id_usuario,
        datos,
        diagnostico
    )

    # Guardar el diagnóstico técnico generado por la IA
    solicitud.diagnostico_ia = diagnostico.get("diagnostico_ia") or None
    db.commit()
    db.refresh(solicitud)

    if turno_elegido:
        solicitud.turno_solicitado = turno_elegido
        # Calcular la fecha concreta del trabajo a partir del turno elegido.
        # Es clave para la agenda del plomero y el detalle del día.
        solicitud.fecha_trabajo = _calcular_fecha_trabajo(turno_elegido)
        db.commit()
        db.refresh(solicitud)

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

    # Notificación in-app a cada plomero invitado
    es_urgente = (diagnostico.get("urgencia_ia") == "URGENTE")
    for p in plomeros:
        notificaciones_inapp.notificar_plomero(
            db,
            id_plomero=p.id_plomero,
            tipo="urgencia" if es_urgente else "nueva_solicitud",
            titulo="Nueva urgencia 🚨" if es_urgente else "Nueva solicitud",
            mensaje=(
                f"{'URGENTE — ' if es_urgente else ''}"
                f"{(diagnostico.get('etiqueta_ia') or 'Trabajo de plomería')}. "
                f"Tenés {'30 minutos' if es_urgente else '3 horas'} para responder."
            ),
            id_solicitud=solicitud.id_solicitud,
        )

    return _to_response(
        solicitud_repository.obtener_por_id(
            db,
            solicitud.id_solicitud
        )
    )
def _trabajo_vencido_sin_cerrar(db: Session, id_plomero: int):
    """Devuelve un trabajo del plomero en curso cuya fecha YA pasó y sigue sin
    cerrar (o None). Los trabajos futuros NO cuentan: solo bloquea el vencido."""
    hoy = datetime.now().date()
    for s in solicitud_repository.listar_por_plomero(db, id_plomero):
        if (
            s.id_plomero == id_plomero
            and s.estado in (EstadoSolicitud.EN_PROGRESO, EstadoSolicitud.EN_CAMINO)
            and s.fecha_trabajo
            and s.fecha_trabajo.date() < hoy
        ):
            return s
    return None


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

    # Un plomero suspendido no puede aceptar trabajos (con reactivación automática).
    plomero_actor = plomero_repository.buscar_por_id(db, id_plomero)
    if moderacion.esta_suspendido(db, plomero_actor):
        raise HTTPException(
            status_code=403,
            detail=moderacion.mensaje_suspension(plomero_actor),
        )

    # No puede tomar un trabajo nuevo si tiene uno VENCIDO sin cerrar (fecha pasada).
    # Los trabajos futuros ya aceptados no bloquean.
    if _trabajo_vencido_sin_cerrar(db, id_plomero):
        raise HTTPException(
            status_code=400,
            detail=(
                "Tenés un trabajo sin cerrar cuya fecha ya pasó. "
                "Finalizalo y cargá la boleta antes de tomar uno nuevo."
            ),
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

    # Avisar al cliente que su solicitud fue aceptada
    nombre_plomero = (
        f"{solicitud.plomero.nombre} {solicitud.plomero.apellido}"
        if solicitud.plomero else "Un profesional"
    )
    notificaciones_inapp.notificar_cliente(
        db,
        id_usuario=solicitud.id_usuario,
        tipo="solicitud_aceptada",
        titulo="Solicitud aceptada ✅",
        mensaje=f"{nombre_plomero} aceptó tu solicitud y ya tiene los datos del trabajo.",
        id_solicitud=id_solicitud,
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

    # Ya nadie puede aceptar.
    #  - Si todavía quedan reintentos → SIN_RESPUESTA: el cliente vuelve a buscar
    #    (excluyendo a los que rechazaron) o cancela.
    #  - Si ya se agotaron los 3 reintentos → la CERRAMOS automáticamente
    #    (sin penalización; no depende de que el cliente toque nada).
    intentos = solicitud.intentos_reasignacion or 0

    if intentos >= MAX_RONDAS_BUSQUEDA:
        solicitud_repository.cambiar_estado(
            db, id_solicitud, EstadoSolicitud.CANCELADA
        )
        notificaciones_inapp.notificar_cliente(
            db,
            id_usuario=solicitud.id_usuario,
            tipo="sin_respuesta",
            titulo="No encontramos un profesional",
            mensaje=(
                "Disculpá las molestias: probamos con varios profesionales y "
                "ninguno pudo tomar tu pedido. Cerramos esta solicitud; "
                "podés volver a intentarlo más tarde."
            ),
            id_solicitud=id_solicitud,
        )
        return {
            "mensaje": "Se agotaron los reintentos. Solicitud cerrada automáticamente."
        }

    solicitud_repository.cambiar_estado(
        db, id_solicitud, EstadoSolicitud.SIN_RESPUESTA
    )
    quedan = MAX_RONDAS_BUSQUEDA - intentos
    notificaciones_inapp.notificar_cliente(
        db,
        id_usuario=solicitud.id_usuario,
        tipo="sin_respuesta",
        titulo="Tu pedido no fue tomado",
        mensaje=(
            "Los profesionales que elegiste no pudieron tomar tu pedido. "
            f"Volvé a buscar otros (te queda{'n' if quedan != 1 else ''} {quedan} "
            f"intento{'s' if quedan != 1 else ''}) o cancelá la solicitud."
        ),
        id_solicitud=id_solicitud,
    )

    return {
        "mensaje": "Todos rechazaron. El cliente puede volver a buscar o cancelar."
    }


# ─────────────────────────────────────────────
# REINTENTAR — el cliente vuelve a buscar en la MISMA solicitud
# ─────────────────────────────────────────────
def reintentar(
    db: Session,
    id_solicitud: int,
    id_usuario: int,
    ids_plomeros: list[int],
    turnos_por_plomero: dict | None = None,
):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")
    if solicitud.estado not in (
        EstadoSolicitud.SIN_RESPUESTA,
        EstadoSolicitud.PENDIENTE,
    ):
        raise HTTPException(
            status_code=400,
            detail="Solo se puede volver a buscar en una solicitud abierta sin respuesta",
        )
    if (solicitud.intentos_reasignacion or 0) >= MAX_RONDAS_BUSQUEDA:
        raise HTTPException(
            status_code=400,
            detail="Se agotaron los reintentos. Cancelá la solicitud para cerrarla.",
        )

    # Excluir a quienes ya fueron contactados en ESTA solicitud (rechazaron o no respondieron)
    ya_contactados = solicitud_plomero_repository.obtener_contactados(db, id_solicitud)
    nuevos_ids = [pid for pid in (ids_plomeros or []) if pid not in ya_contactados]
    if not nuevos_ids:
        raise HTTPException(
            status_code=400,
            detail="Elegí profesionales nuevos: los anteriores ya fueron contactados.",
        )

    # Turno (mismo criterio que crear: se toma el del primer seleccionado)
    turnos = turnos_por_plomero or {}
    turno_elegido = turnos.get(str(nuevos_ids[0]))
    if turno_elegido:
        solicitud.turno_solicitado = turno_elegido
        solicitud.fecha_trabajo = _calcular_fecha_trabajo(turno_elegido)

    solicitud_plomero_repository.crear_invitaciones_bulk(db, id_solicitud, nuevos_ids)

    solicitud.intentos_reasignacion = (solicitud.intentos_reasignacion or 0) + 1
    solicitud.fecha_ultimo_envio = datetime.now()
    solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.PENDIENTE)
    db.commit()
    db.refresh(solicitud)

    plomeros = [
        p for p in (plomero_repository.buscar_por_id(db, pid) for pid in nuevos_ids) if p
    ]
    diagnostico = {
        "etiqueta_ia": solicitud.etiqueta_ia,
        "urgencia_ia": solicitud.urgencia_ia,
        "presupuesto_min": solicitud.presupuesto_min,
        "presupuesto_max": solicitud.presupuesto_max,
    }
    try:
        notificacion_service.notificar_plomeros(
            plomeros=plomeros,
            solicitud_id=solicitud.id_solicitud,
            descripcion=solicitud.descripcion_raw,
            diagnostico=diagnostico,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"No se pudo notificar (email) en reintentar: {e}")

    es_urgente = (solicitud.urgencia_ia == "URGENTE")
    for p in plomeros:
        notificaciones_inapp.notificar_plomero(
            db,
            id_plomero=p.id_plomero,
            tipo="urgencia" if es_urgente else "nueva_solicitud",
            titulo="Nueva urgencia 🚨" if es_urgente else "Nueva solicitud",
            mensaje=(
                f"{'URGENTE — ' if es_urgente else ''}"
                f"{(solicitud.etiqueta_ia or 'Trabajo de plomería')}. "
                f"Tenés {'30 minutos' if es_urgente else '3 horas'} para responder."
            ),
            id_solicitud=solicitud.id_solicitud,
        )

    return _to_response(
        solicitud_repository.obtener_por_id(db, solicitud.id_solicitud)
    )


# ─────────────────────────────────────────────
# BORRADOR — el cliente pidió diagnóstico pero todavía no envió a nadie
# ─────────────────────────────────────────────
BORRADOR_VENCE_HORAS = 48


def crear_o_actualizar_borrador(db: Session, descripcion: str, id_usuario: int):
    """
    El cliente pidió un diagnóstico. Guardamos (o actualizamos) UN borrador por
    usuario con el diagnóstico, para que la búsqueda no se pierda al navegar.
    Queda abierto hasta que lo envía, lo cancela o vence a las 48hs.
    """
    diagnostico = ia_service.analizar_descripcion(descripcion)
    if not diagnostico.get("valido", True):
        return {"diagnostico": diagnostico, "borrador": None}

    usuario = usuario_repository.buscar_por_id(db, id_usuario)
    if moderacion.esta_suspendido(db, usuario):
        raise HTTPException(status_code=403, detail=moderacion.mensaje_suspension(usuario))

    # Reutilizamos el borrador abierto del usuario si ya existe (uno por vez).
    existente = next(
        (
            s for s in solicitud_repository.listar_por_usuario(db, id_usuario)
            if s.estado == EstadoSolicitud.BORRADOR
        ),
        None,
    )

    if existente:
        solicitud = existente
        solicitud.descripcion_raw = descripcion
        solicitud.fecha = datetime.now()   # reinicia el reloj de 48hs
    else:
        solicitud = Solicitud(
            id_usuario       = id_usuario,
            descripcion_raw  = descripcion,
            localidad_evento = (getattr(usuario, "localidad", None) or "Sin especificar"),
            latitud_evento   = getattr(usuario, "latitud", None),
            longitud_evento  = getattr(usuario, "longitud", None),
            estado           = EstadoSolicitud.BORRADOR,
        )
        db.add(solicitud)

    solicitud.etiqueta_ia     = diagnostico.get("etiqueta_ia")
    solicitud.urgencia_ia     = diagnostico.get("urgencia_ia")
    solicitud.diagnostico_ia  = diagnostico.get("diagnostico_ia")
    solicitud.presupuesto_min = diagnostico.get("presupuesto_min")
    solicitud.presupuesto_max = diagnostico.get("presupuesto_max")
    db.commit()
    db.refresh(solicitud)

    return {
        "diagnostico": diagnostico,
        "borrador": _to_response(solicitud),
    }


def confirmar_borrador(
    db: Session,
    id_solicitud: int,
    id_usuario: int,
    ids_plomeros: list[int],
    turnos_por_plomero: dict | None = None,
):
    """El cliente envía el borrador a los plomeros elegidos: BORRADOR → PENDIENTE."""
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")
    if solicitud.estado != EstadoSolicitud.BORRADOR:
        raise HTTPException(status_code=400, detail="La solicitud ya fue enviada")
    if not ids_plomeros:
        raise HTTPException(status_code=400, detail="Elegí al menos un profesional")

    turnos = turnos_por_plomero or {}
    turno_elegido = turnos.get(str(ids_plomeros[0]))
    if turno_elegido:
        solicitud.turno_solicitado = turno_elegido
        solicitud.fecha_trabajo = _calcular_fecha_trabajo(turno_elegido)

    solicitud_plomero_repository.crear_invitaciones_bulk(db, id_solicitud, ids_plomeros)
    solicitud.fecha_ultimo_envio = datetime.now()
    solicitud_repository.cambiar_estado(db, id_solicitud, EstadoSolicitud.PENDIENTE)
    db.commit()
    db.refresh(solicitud)

    plomeros = [
        p for p in (plomero_repository.buscar_por_id(db, pid) for pid in ids_plomeros) if p
    ]
    diagnostico = {
        "etiqueta_ia": solicitud.etiqueta_ia,
        "urgencia_ia": solicitud.urgencia_ia,
        "presupuesto_min": solicitud.presupuesto_min,
        "presupuesto_max": solicitud.presupuesto_max,
    }
    try:
        notificacion_service.notificar_plomeros(
            plomeros=plomeros,
            solicitud_id=solicitud.id_solicitud,
            descripcion=solicitud.descripcion_raw,
            diagnostico=diagnostico,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"No se pudo notificar (email) al confirmar borrador: {e}")

    es_urgente = (solicitud.urgencia_ia == "URGENTE")
    for p in plomeros:
        notificaciones_inapp.notificar_plomero(
            db,
            id_plomero=p.id_plomero,
            tipo="urgencia" if es_urgente else "nueva_solicitud",
            titulo="Nueva urgencia 🚨" if es_urgente else "Nueva solicitud",
            mensaje=(
                f"{'URGENTE — ' if es_urgente else ''}"
                f"{(solicitud.etiqueta_ia or 'Trabajo de plomería')}. "
                f"Tenés {'30 minutos' if es_urgente else '3 horas'} para responder."
            ),
            id_solicitud=solicitud.id_solicitud,
        )

    return _to_response(solicitud_repository.obtener_por_id(db, solicitud.id_solicitud))


def _cerrar_borradores_vencidos(db: Session, id_usuario: int):
    """Limpieza perezosa: cierra borradores con +48hs sin enviarse."""
    limite = datetime.now() - timedelta(hours=BORRADOR_VENCE_HORAS)
    for s in solicitud_repository.listar_por_usuario(db, id_usuario):
        if s.estado == EstadoSolicitud.BORRADOR and s.fecha and s.fecha < limite:
            solicitud_repository.cambiar_estado(db, s.id_solicitud, EstadoSolicitud.CANCELADA)
            notificaciones_inapp.notificar_cliente(
                db,
                id_usuario=id_usuario,
                tipo="borrador_vencido",
                titulo="Cerramos tu pedido en preparación",
                mensaje=(
                    "Pasaron 48hs desde que pediste el diagnóstico sin enviar la "
                    "solicitud a ningún profesional, así que la cerramos. "
                    "Podés empezar una nueva cuando quieras."
                ),
                id_solicitud=s.id_solicitud,
            )


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
        and datetime.now().date() < solicitud.fecha_trabajo.date()
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Solo podés marcar EN CAMINO "
                "el día del trabajo o después"
            )
        )

    solicitud = solicitud_repository.cambiar_estado(
        db,
        id_solicitud,
        EstadoSolicitud.EN_CAMINO
    )

    notificaciones_inapp.notificar_cliente(
        db,
        id_usuario=solicitud.id_usuario,
        tipo="en_camino",
        titulo="El profesional está en camino 🚗",
        mensaje="Tu plomero marcó que ya está en camino al domicilio.",
        id_solicitud=id_solicitud,
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

    # La boleta es OBLIGATORIA: no se puede finalizar sin cargar al menos un ítem
    # (materiales y/o mano de obra). Cada ítem ya fue validado al cargarse.
    total_boleta = material_repository.total_por_solicitud(db, id_solicitud)
    if not total_boleta or total_boleta <= 0:
        raise HTTPException(
            status_code=400,
            detail="Cargá la boleta (materiales y mano de obra) antes de finalizar el trabajo.",
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

    # Arranca el plazo de 72hs para que ambos califiquen
    _cal_service.activar_periodo_calificacion(db, id_solicitud)

    notificaciones_inapp.notificar_cliente(
        db,
        id_usuario=solicitud.id_usuario,
        tipo="trabajo_finalizado",
        titulo="Trabajo finalizado 🏁",
        mensaje="El trabajo fue marcado como finalizado. Tenés 72 horas para calificar al profesional.",
        id_solicitud=id_solicitud,
    )

    return _to_response(solicitud)

def reprogramar(db: Session, id_solicitud: int, actor: dict, nueva_fecha):
    """
    Reprograma la fecha/hora del trabajo (cuando cliente y plomero lo acuerdan).
    Lo puede hacer cualquiera de los dos mientras el trabajo está en curso.
    """
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="No encontrada")
    if actor["id"] not in [solicitud.id_usuario, solicitud.id_plomero]:
        raise HTTPException(status_code=403, detail="No autorizado")
    if solicitud.estado not in (EstadoSolicitud.EN_PROGRESO, EstadoSolicitud.EN_CAMINO):
        raise HTTPException(status_code=400, detail="Solo se puede reprogramar un trabajo en curso")
    # Debe haber comunicación previa: ambos escribieron en el chat.
    if not mensaje_repository.hubo_intercambio(db, id_solicitud):
        raise HTTPException(
            status_code=400,
            detail="Coordiná el nuevo horario por el chat antes de reprogramar (deben escribir ambos)",
        )

    solicitud.fecha_trabajo = nueva_fecha
    db.commit()
    db.refresh(solicitud)

    if actor["role"] == "plomero":
        notificaciones_inapp.notificar_cliente(
            db, id_usuario=solicitud.id_usuario, tipo="reprogramado",
            titulo="Visita reprogramada 🗓️",
            mensaje="El profesional reprogramó el horario de la visita.",
            id_solicitud=id_solicitud,
        )
    else:
        notificaciones_inapp.notificar_plomero(
            db, id_plomero=solicitud.id_plomero, tipo="reprogramado",
            titulo="Visita reprogramada 🗓️",
            mensaje="El cliente propuso un nuevo horario para la visita.",
            id_solicitud=id_solicitud,
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

    estados_cancelables = (
        EstadoSolicitud.BORRADOR,        # pedido en preparación → cerrar sin penalización
        EstadoSolicitud.PENDIENTE,
        EstadoSolicitud.EN_PROGRESO,
        EstadoSolicitud.EN_CAMINO,
        EstadoSolicitud.REASIGNACION_PENDIENTE,
        EstadoSolicitud.SIN_RESPUESTA,   # todos rechazaron → cerrar sin penalización
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

    # Avisar al plomero asignado que el cliente canceló
    if habia_plomero and not en_reasignacion:
        notificaciones_inapp.notificar_plomero(
            db,
            id_plomero=solicitud.id_plomero,
            tipo="cancelada_cliente",
            titulo="El cliente canceló ❌",
            mensaje="El cliente canceló un trabajo que tenías asignado. El día vuelve a estar disponible en tu agenda.",
            id_solicitud=id_solicitud,
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

    notificaciones_inapp.notificar_cliente(
        db,
        id_usuario=solicitud.id_usuario,
        tipo="cancelada_plomero",
        titulo="El profesional canceló ⚠️",
        mensaje="El plomero canceló el trabajo. Podés buscar nuevos profesionales sin volver a crear la solicitud.",
        id_solicitud=id_solicitud,
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

def _con_flags_calificacion(db, s, r):
    """Agrega a la respuesta si cada parte ya calificó y el total de la boleta."""
    r["cliente_califico"] = calificacion_repository.ya_califico(db, s.id_solicitud, "cliente")
    r["plomero_califico"] = calificacion_repository.ya_califico(db, s.id_solicitud, "plomero")
    r["total_boleta"] = material_repository.total_por_solicitud(db, s.id_solicitud)
    # Hubo intercambio en el chat (cliente y plomero escribieron) → habilita reprogramar
    r["comunicacion_ok"] = mensaje_repository.hubo_intercambio(db, s.id_solicitud)
    return r


def listar_por_usuario(db: Session, id_usuario: int):
    _cerrar_borradores_vencidos(db, id_usuario)   # cierra borradores +48hs sin enviar
    return [
        _con_flags_calificacion(db, s, _to_response(s))
        for s in solicitud_repository.listar_por_usuario(db, id_usuario)
    ]


def _avisar_trabajos_vencidos(db, id_plomero, solicitudes):
    """Notifica UNA vez por cada trabajo vencido sin cerrar (usa una bandera
    para no repetir el aviso en cada refresco)."""
    hoy = datetime.now().date()
    hubo_cambio = False
    for s in solicitudes:
        if (
            s.id_plomero == id_plomero
            and s.estado in (EstadoSolicitud.EN_PROGRESO, EstadoSolicitud.EN_CAMINO)
            and s.fecha_trabajo and s.fecha_trabajo.date() < hoy
            and not s.aviso_cierre_enviado
        ):
            notificaciones_inapp.notificar_plomero(
                db,
                id_plomero=id_plomero,
                tipo="pendiente_cierre",
                titulo="⏰ Trabajo pendiente de cierre",
                mensaje=(
                    "Tenés un trabajo cuya fecha ya pasó y sigue sin cerrar. "
                    "Finalizalo y cargá la boleta. No vas a poder tomar nuevos "
                    "trabajos hasta cerrarlo."
                ),
                id_solicitud=s.id_solicitud,
            )
            s.aviso_cierre_enviado = True
            hubo_cambio = True
    if hubo_cambio:
        db.commit()


def listar_por_plomero(db: Session, id_plomero: int):
    solicitudes = solicitud_repository.listar_por_plomero(db, id_plomero)
    _avisar_trabajos_vencidos(db, id_plomero, solicitudes)
    return [
        _con_flags_calificacion(db, s, _to_response(s))
        for s in solicitudes
    ]


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