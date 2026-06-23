# services/notificaciones_inapp.py
"""
Notificaciones in-app persistentes (pestaña "Alertas" de ambos actores).

Separado de notificacion_service (que manda mails a plomeros) para respetar
responsabilidad única: este módulo solo escribe/lee la tabla `notificaciones`.
Se invoca desde solicitud_service y mensajeria_service en cada transición
relevante. Los errores nunca interrumpen el flujo principal del negocio.
"""
import logging

from models.notificacion import Notificacion
from repositories import notificacion_repository

logger = logging.getLogger(__name__)


def crear(
    db,
    destinatario_id: int,
    destinatario_rol: str,
    tipo: str,
    titulo: str,
    mensaje: str,
    id_solicitud: int | None = None,
):
    """Crea una notificación. Si falla, loguea y sigue (best-effort)."""
    if not destinatario_id or not destinatario_rol:
        return None
    try:
        notif = Notificacion(
            destinatario_id=destinatario_id,
            destinatario_rol=destinatario_rol,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            id_solicitud=id_solicitud,
        )
        return notificacion_repository.crear(db, notif)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[notificaciones_inapp] No se pudo crear notificación: {e}")
        try:
            db.rollback()
        except Exception:
            pass
        return None


# ── Helpers semánticos por actor ────────────────────────────────────────────

def notificar_cliente(db, id_usuario, tipo, titulo, mensaje, id_solicitud=None):
    return crear(db, id_usuario, "usuario", tipo, titulo, mensaje, id_solicitud)


def notificar_plomero(db, id_plomero, tipo, titulo, mensaje, id_solicitud=None):
    return crear(db, id_plomero, "plomero", tipo, titulo, mensaje, id_solicitud)


def listar(db, destinatario_id, destinatario_rol):
    return notificacion_repository.listar_por_destinatario(
        db, destinatario_id, destinatario_rol
    )


def marcar_leida(db, id_notificacion, destinatario_id, destinatario_rol):
    notif = notificacion_repository.obtener_por_id(db, id_notificacion)
    if not notif:
        return None
    # Seguridad: solo el dueño puede marcar su notificación
    if notif.destinatario_id != destinatario_id or notif.destinatario_rol != destinatario_rol:
        return None
    return notificacion_repository.marcar_leida(db, notif)


def marcar_todas_leidas(db, destinatario_id, destinatario_rol):
    return notificacion_repository.marcar_todas_leidas(
        db, destinatario_id, destinatario_rol
    )


def eliminar_todas(db, destinatario_id, destinatario_rol):
    return notificacion_repository.eliminar_todas(
        db, destinatario_id, destinatario_rol
    )
