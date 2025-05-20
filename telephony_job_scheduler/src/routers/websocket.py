from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from infrastructure.websockets.connection_manager import ConnectionManager

router = APIRouter(tags=["websocket"])
connection_manager = ConnectionManager()


@router.websocket("/ws/jobs")
async def websocket_endpoint(websocket: WebSocket):
    user_id = "public"
    await connection_manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket, user_id)
