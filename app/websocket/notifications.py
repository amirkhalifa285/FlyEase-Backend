"""
WebSocket notification management for FlyEase.
Provides ConnectionManager for robust connection handling.
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections with proper cleanup and user tracking.
    Handles disconnections gracefully and supports user-specific messaging.
    """
    
    def __init__(self):
        # Map user_id -> WebSocket connection
        self.active_connections: Dict[int, WebSocket] = {}
        # Anonymous connections (no user_id)
        self.anonymous_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None):
        """Accept a WebSocket connection."""
        await websocket.accept()
        
        if user_id:
            # Disconnect existing connection for this user (if any)
            if user_id in self.active_connections:
                await self.disconnect(user_id=user_id)
            self.active_connections[user_id] = websocket
            logger.info(f"WebSocket connected: user {user_id}")
        else:
            self.anonymous_connections.append(websocket)
            logger.info("WebSocket connected: anonymous")
    
    async def disconnect(self, websocket: WebSocket = None, user_id: Optional[int] = None):
        """Remove a WebSocket connection."""
        try:
            if user_id and user_id in self.active_connections:
                ws = self.active_connections.pop(user_id)
                await ws.close()
                logger.info(f"WebSocket disconnected: user {user_id}")
            elif websocket and websocket in self.anonymous_connections:
                self.anonymous_connections.remove(websocket)
                await websocket.close()
                logger.info("WebSocket disconnected: anonymous")
        except Exception as e:
            logger.warning(f"Error during WebSocket disconnect: {e}")
    
    async def send_personal_message(self, message: str, user_id: int):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to user {user_id}: {e}")
                await self.disconnect(user_id=user_id)
    
    async def broadcast(self, message: str):
        """Send a message to all connected clients."""
        dead_connections = []
        
        # Broadcast to authenticated users
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception:
                dead_connections.append(("user", user_id))
        
        # Broadcast to anonymous users
        for websocket in self.anonymous_connections:
            try:
                await websocket.send_text(message)
            except Exception:
                dead_connections.append(("anon", websocket))
        
        # Clean up dead connections
        for conn_type, identifier in dead_connections:
            if conn_type == "user":
                self.active_connections.pop(identifier, None)
            else:
                try:
                    self.anonymous_connections.remove(identifier)
                except ValueError:
                    pass
    
    @property
    def connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self.active_connections) + len(self.anonymous_connections)


# Global connection manager instance
manager = ConnectionManager()


# Legacy functions for backwards compatibility
async def connect_user(websocket: WebSocket):
    """Legacy: Accept a WebSocket connection."""
    await manager.connect(websocket)


async def disconnect_user(websocket: WebSocket):
    """Legacy: Remove a WebSocket connection."""
    await manager.disconnect(websocket=websocket)


async def broadcast_message(message: str):
    """Legacy: Send a message to all connections."""
    await manager.broadcast(message)


# WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for notifications."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive by listening for messages
            data = await websocket.receive_text()
            # Echo back for ping/pong or handle commands
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket=websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket=websocket)

