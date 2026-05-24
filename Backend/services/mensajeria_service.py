from fastapi import HTTPException
from schemas.mensaje import MensajeResponse
from models.mensaje import Mensaje
from models.solicitud import EstadoSolicitud
from repositories import mensaje_repository, solicitud_repository


def enviar_mensaje(db, id_solicitud, texto, emisor_id, emisor_rol):

    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no existe")

    # 🔥 regla clave del sistema
    if solicitud.estado != EstadoSolicitud.EN_PROGRESO:
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

    return MensajeResponse.model_validate(mensaje)

def obtener_chat(db, id_solicitud: int):
    return mensaje_repository.listar_por_solicitud(db, id_solicitud)