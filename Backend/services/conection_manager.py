from collections import defaultdict
from typing import List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = defaultdict(list)

    async def connect(self, id_solicitud: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[id_solicitud].append(websocket)

    def disconnect(self, id_solicitud: int, websocket: WebSocket):
        connections = self.active_connections.get(id_solicitud)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        # limpia memoria si queda vacío
        if not connections:
            self.active_connections.pop(id_solicitud, None)

    async def send_to_room(self, id_solicitud: int, message: dict):
        connections = self.active_connections.get(id_solicitud, [])

        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                # si el socket murió, lo limpiás
                connections.remove(ws)


manager = ConnectionManager()