# routers/chat_ws.py

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from database import SessionLocal

from core.auth_ws import decode_token_ws

from services.conection_manager import manager
from services import mensajeria_service

from repositories import solicitud_repository
from models.solicitud import EstadoSolicitud


router = APIRouter()


@router.websocket("/ws/chat/{id_solicitud}")
async def chat_ws(
    websocket: WebSocket,
    id_solicitud: int
):

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    try:
        user = decode_token_ws(token)

    except:
        await websocket.close(code=1008)
        return

    db = SessionLocal()

    solicitud = solicitud_repository.obtener_por_id(
        db,
        id_solicitud
    )

    if not solicitud:
        await websocket.close(code=1008)
        return

    if user["id"] not in [
        solicitud.id_usuario,
        solicitud.id_plomero
    ]:
        await websocket.close(code=1008)
        return

    if solicitud.estado != EstadoSolicitud.EN_PROGRESO:
        await websocket.close(code=1008)
        return

    await manager.connect(
        id_solicitud,
        websocket
    )

    print(f"WS conectado: {id_solicitud}")

    try:

        while True:

            data = await websocket.receive_json()

            if not data.get("texto"):
                continue

            mensaje = mensajeria_service.enviar_mensaje(
                db=db,
                id_solicitud=id_solicitud,
                texto=data["texto"],
                emisor_id=user["id"],
                emisor_rol=user["role"]
            )

            await manager.send_to_room(
                id_solicitud,
                {
                    "id_mensaje": mensaje.id_mensaje,
                    "texto": mensaje.texto,
                    "emisor_id": mensaje.emisor_id,
                    "emisor_rol": mensaje.emisor_rol,
                    "fecha": str(mensaje.fecha)
                }
            )

    except WebSocketDisconnect:

        manager.disconnect(
            id_solicitud,
            websocket
        )

        print(f"WS desconectado: {id_solicitud}")

    finally:
        db.close()