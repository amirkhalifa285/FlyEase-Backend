from fastapi import WebSocket, WebSocketDisconnect
from typing import List

# List to store active WebSocket connections
active_connections: List[WebSocket] = []

async def connect_user(websocket: WebSocket):
    """
    Accept a WebSocket connection and add it to the list of active connections.
    """
    await websocket.accept()
    active_connections.append(websocket)

async def disconnect_user(websocket: WebSocket):
    """
    Remove a WebSocket connection from the list of active connections.
    """
    active_connections.remove(websocket)

async def broadcast_message(message: str):
    """
    Send a message to all active WebSocket connections.
    """
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except WebSocketDisconnect:
            await disconnect_user(connection)

# WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket):
    await connect_user(websocket)
    try:
        while True:
            # Keep the connection alive by listening for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        await disconnect_user(websocket)
