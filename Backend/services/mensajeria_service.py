from fastapi import HTTPException
from schemas.mensaje import MensajeResponse
from models.mensaje import Mensaje
from models.solicitud import EstadoSolicitud
from repositories import mensaje_repository, solicitud_repository
from services import notificaciones_inapp


# Estados en los que el chat está habilitado: hay un plomero asignado y el
# trabajo sigue en curso. Incluye EN_CAMINO para permitir avisos de "llego
# tarde" / "puedo ir más tarde" mientras el profesional va al domicilio.
ESTADOS_CHAT_ACTIVO = {
    EstadoSolicitud.EN_PROGRESO,
    EstadoSolicitud.EN_CAMINO,
}


def enviar_mensaje(db, id_solicitud, texto, emisor_id, emisor_rol):

    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no existe")

    # 🔥 regla clave del sistema: el chat solo vive mientras hay trabajo en curso
    if solicitud.estado not in ESTADOS_CHAT_ACTIVO:
        raise HTTPException(status_code=400, detail="Chat no habilitado")

    # 🔒 seguridad
    if emisor_id not in [solicitud.id_usuario, solicitud.id_plomero]:
        raise HTTPException(status_code=403, detail="No autorizado")

    mensaje = Mensaje(
        id_solicitud=id_solicitud,
        emisor_id=emisor_id,
        emisor_rol=emisor_rol,
        texto=texto
    )

    db.add(mensaje)
    db.commit()
    db.refresh(mensaje)

    # Notificar a la contraparte sobre el nuevo mensaje
    _notificar_contraparte(db, solicitud, emisor_rol, texto)

    return MensajeResponse.model_validate(mensaje)


def _notificar_contraparte(db, solicitud, emisor_rol, texto):
    """Crea una notificación in-app para quien NO envió el mensaje."""
    preview = (texto or "").strip()
    if len(preview) > 60:
        preview = preview[:57] + "…"

    if emisor_rol == "usuario":
        # El cliente escribió → avisar al plomero
        nombre = (
            f"{solicitud.usuario.nombre}"
            if solicitud.usuario else "El cliente"
        )
        notificaciones_inapp.notificar_plomero(
            db,
            id_plomero=solicitud.id_plomero,
            tipo="mensaje",
            titulo=f"💬 Mensaje de {nombre}",
            mensaje=preview or "Te enviaron un mensaje.",
            id_solicitud=solicitud.id_solicitud,
        )
    else:
        # El plomero escribió → avisar al cliente
        nombre = (
            f"{solicitud.plomero.nombre}"
            if solicitud.plomero else "El profesional"
        )
        notificaciones_inapp.notificar_cliente(
            db,
            id_usuario=solicitud.id_usuario,
            tipo="mensaje",
            titulo=f"💬 Mensaje de {nombre}",
            mensaje=preview or "Te enviaron un mensaje.",
            id_solicitud=solicitud.id_solicitud,
        )


def obtener_chat(db, id_solicitud: int):
    mensajes = mensaje_repository.listar_por_solicitud(db, id_solicitud)
    return [MensajeResponse.model_validate(m) for m in mensajes]
