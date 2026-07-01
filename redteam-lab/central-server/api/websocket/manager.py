import asyncio
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger("websocket.manager")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.campaign_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, campaign_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if campaign_id:
            if campaign_id not in self.campaign_connections:
                self.campaign_connections[campaign_id] = []
            self.campaign_connections[campaign_id].append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, campaign_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if campaign_id and campaign_id in self.campaign_connections:
            if websocket in self.campaign_connections[campaign_id]:
                self.campaign_connections[campaign_id].remove(websocket)

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WS: {e}")

    async def broadcast_to_campaign(self, campaign_id: str, message: dict):
        """Send message to clients viewing a specific campaign."""
        if campaign_id in self.campaign_connections:
            for connection in self.campaign_connections[campaign_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to campaign WS: {e}")

manager = ConnectionManager()
