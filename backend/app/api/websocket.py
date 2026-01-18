"""
WebSocket Real-Time Monitoring API

Provides real-time updates for exam sessions, risk scores, and alerts.
"""

from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
import json
import asyncio
from datetime import datetime

from app.core.auth import get_current_user, User
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for real-time monitoring."""
    
    def __init__(self):
        # Store active connections by session_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store admin connections (monitor all sessions)
        self.admin_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, session_id: str = None, is_admin: bool = False):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        
        if is_admin:
            self.admin_connections.add(websocket)
            logger.info("Admin WebSocket connected", admin_count=len(self.admin_connections))
        elif session_id:
            if session_id not in self.active_connections:
                self.active_connections[session_id] = set()
            self.active_connections[session_id].add(websocket)
            logger.info("Session WebSocket connected", session_id=session_id)
    
    def disconnect(self, websocket: WebSocket, session_id: str = None, is_admin: bool = False):
        """Remove a WebSocket connection."""
        if is_admin and websocket in self.admin_connections:
            self.admin_connections.remove(websocket)
            logger.info("Admin WebSocket disconnected")
        elif session_id and session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
                logger.info("Session WebSocket disconnected", session_id=session_id)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error("Failed to send WebSocket message", error=str(e))
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast a message to all connections monitoring a session."""
        if session_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.active_connections[session_id].discard(conn)
    
    async def broadcast_to_admins(self, message: dict):
        """Broadcast a message to all admin connections."""
        disconnected = set()
        for connection in self.admin_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected admins
        for conn in disconnected:
            self.admin_connections.discard(conn)
    
    async def broadcast_alert(self, session_id: str, alert_data: dict):
        """Broadcast an alert for a session to both session and admin connections."""
        message = {
            "type": "alert",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            **alert_data
        }
        
        # Send to session-specific connections
        await self.broadcast_to_session(session_id, message)
        
        # Send to admin connections
        await self.broadcast_to_admins(message)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/monitor/{session_id}")
async def websocket_session_monitor(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint for monitoring a specific session.
    
    Provides real-time updates for:
    - Risk score changes
    - Event logging
    - Analysis results
    - Alerts and flags
    """
    await manager.connect(websocket, session_id=session_id)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    # Respond to ping with pong
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif action == "subscribe":
                    # Client confirming subscription
                    await websocket.send_json({
                        "type": "subscribed",
                        "session_id": session_id,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id=session_id)


@router.websocket("/ws/admin")
async def websocket_admin_monitor(websocket: WebSocket):
    """
    WebSocket endpoint for admin monitoring (all sessions).
    
    Provides real-time updates for all active sessions.
    """
    await manager.connect(websocket, is_admin=True)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif action == "subscribe_all":
                    await websocket.send_json({
                        "type": "subscribed",
                        "mode": "admin",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, is_admin=True)


# Helper functions for broadcasting updates

async def broadcast_risk_update(session_id: str, risk_score: float, risk_level: str):
    """Broadcast a risk score update."""
    await manager.broadcast_to_session(session_id, {
        "type": "risk_update",
        "session_id": session_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Also send to admins
    await manager.broadcast_to_admins({
        "type": "risk_update",
        "session_id": session_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_session_status(session_id: str, status: str, details: dict = None):
    """Broadcast a session status change."""
    message = {
        "type": "status_update",
        "session_id": session_id,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        message["details"] = details
    
    await manager.broadcast_to_session(session_id, message)
    await manager.broadcast_to_admins(message)


async def broadcast_alert(session_id: str, alert_type: str, message: str, severity: str = "warning"):
    """Broadcast an alert."""
    await manager.broadcast_alert(session_id, {
        "alert_type": alert_type,
        "message": message,
        "severity": severity
    })


# Background task for periodic updates
async def periodic_heartbeat():
    """Send periodic heartbeat to all connections."""
    while True:
        await asyncio.sleep(30)  # Every 30 seconds
        
        message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all admin connections
        await manager.broadcast_to_admins(message)
