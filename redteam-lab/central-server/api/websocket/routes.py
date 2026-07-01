from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.websocket.manager import manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, campaign_id: str = None):
    await manager.connect(websocket, campaign_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages from frontend if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, campaign_id)
