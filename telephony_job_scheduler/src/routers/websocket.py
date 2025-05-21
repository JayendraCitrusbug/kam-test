from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from infrastructure.websockets.connection_manager import ConnectionManager

router = APIRouter(tags=["websocket"])
connection_manager = ConnectionManager()


@router.websocket("/ws/jobs")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections for job updates.

    This endpoint manages WebSocket connections, allowing clients to receive
    real-time job updates. Upon connection, the WebSocket is associated with
    a user identifier and added to the active connections. The connection
    remains open to continuously listen for incoming messages, and is closed
    when a WebSocket disconnection event occurs.

    Args:
        websocket (WebSocket): The WebSocket connection instance for the client.

    Raises:
        WebSocketDisconnect: Raised when the client disconnects, ensuring
        proper cleanup of the active connection.
    """

    user_id = "public"
    await connection_manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket, user_id)
