import logging
from asyncio import Lock
from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.lock = Lock()
        self._initialized = True

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        async with self.lock:
            self.active_connections[user_id].append(websocket)
        logger.info("WebSocket connected: %s", websocket.client)

    async def disconnect(self, websocket: WebSocket, user_id: str):
        async with self.lock:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        logger.info("WebSocket disconnected: %s", websocket.client)

    async def broadcast(self, data: dict) -> None:
        async with self.lock:
            connections_snapshot = {
                user_id: conns[:] for user_id, conns in self.active_connections.items()
            }

        failed_connections: List[tuple[str, WebSocket]] = []

        for user_id, conns in connections_snapshot.items():
            for conn in conns:
                try:
                    await conn.send_json(data)
                except Exception as e:
                    logger.warning(
                        "WebSocket send failed for user_id=%s: %s", user_id, str(e)
                    )
                    failed_connections.append((user_id, conn))

        for user_id, conn in failed_connections:
            await self.disconnect(conn, user_id)
