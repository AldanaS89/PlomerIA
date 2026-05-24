# routers/chat_ws.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.conection_manager import manager
from services import mensajeria_service
from database import SessionLocal
from core.auth_ws import decode_token_ws

router = APIRouter()


@router.websocket("/ws/chat/{id_solicitud}")
async def chat_ws(websocket: WebSocket, id_solicitud: int):

    # 1. autenticar (token query param)
    token = websocket.query_params.get("token")
    user = decode_token_ws(token)

    db = SessionLocal()

    await manager.connect(id_solicitud, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            # data = { "texto": "hola" }

            mensaje = mensajeria_service.enviar_mensaje(
                db=db,
                id_solicitud=id_solicitud,
                texto=data["texto"],
                emisor_id=user["id"],
                emisor_rol=user["role"]
            )

            # 2. broadcast en tiempo real
            await manager.send_to_room(id_solicitud, {
                "id_mensaje": mensaje.id,
                "texto": mensaje.texto,
                "emisor_id": mensaje.emisor_id,
                "emisor_rol": mensaje.emisor_rol,
                "fecha": str(mensaje.fecha)
            })

    except WebSocketDisconnect:
        manager.disconnect(id_solicitud, websocket)
    finally:
        db.close()