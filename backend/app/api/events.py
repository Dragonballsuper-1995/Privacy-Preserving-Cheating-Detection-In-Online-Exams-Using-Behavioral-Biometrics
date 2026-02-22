"""
Events API - Handles behavioral event logging from the frontend.
Captures keystrokes, paste events, focus/blur, etc.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import json
import os

from app.core.config import settings

router = APIRouter()


class KeyEvent(BaseModel):
    """Keyboard event (keydown/keyup)."""
    type: str  # 'keydown' or 'keyup'
    key: str
    code: str
    timestamp: float
    shift: bool = False
    ctrl: bool = False
    alt: bool = False


class PasteEvent(BaseModel):
    """Paste event."""
    type: str = "paste"
    content_length: int
    timestamp: float


class FocusEvent(BaseModel):
    """Focus/blur event."""
    type: str  # 'focus' or 'blur'
    timestamp: float


class BehaviorEvent(BaseModel):
    """Union type for all behavior events."""
    session_id: str
    question_id: str
    event_type: str  # 'key', 'paste', 'focus'
    data: dict
    timestamp: float


class EventBatch(BaseModel):
    """Batch of events from frontend."""
    session_id: str
    events: List[BehaviorEvent]


class EventLogResponse(BaseModel):
    """Response for event logging."""
    success: bool
    events_received: int
    session_id: str


@router.post("/log", response_model=EventLogResponse)
async def log_events(batch: EventBatch):
    """
    Log a batch of behavioral events from the exam frontend.
    Events are stored in JSONL format for later processing.
    """
    # Validate batch size
    if len(batch.events) > settings.max_batch_size:
        raise HTTPException(
            status_code=422,
            detail=f"Batch too large: {len(batch.events)} events (max {settings.max_batch_size})"
        )

    try:
        # Create session log file path
        log_file = os.path.join(
            settings.event_logs_dir, 
            f"session_{batch.session_id}.jsonl"
        )
        
        # Append events to JSONL file
        with open(log_file, 'a') as f:
            for event in batch.events:
                event_data = {
                    "session_id": event.session_id,
                    "question_id": event.question_id,
                    "event_type": event.event_type,
                    "data": event.data,
                    "timestamp": event.timestamp,
                    "logged_at": datetime.now(timezone.utc).isoformat()
                }
                f.write(json.dumps(event_data) + "\n")

        # Broadcast live update to admin WebSocket clients
        try:
            from app.api.websocket import broadcast_session_status
            await broadcast_session_status(
                batch.session_id,
                "events_received",
                {"event_count": len(batch.events)}
            )
        except Exception:
            pass  # Don't fail the request if WS broadcast fails

        return EventLogResponse(
            success=True,
            events_received=len(batch.events),
            session_id=batch.session_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_events(session_id: str, limit: int = 1000):
    """Retrieve events for a specific session."""
    log_file = os.path.join(settings.event_logs_dir, f"session_{session_id}.jsonl")
    
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="Session not found")
    
    events = []
    with open(log_file, 'r') as f:
        for line in f:
            if len(events) >= limit:
                break
            events.append(json.loads(line))
    
    return {"session_id": session_id, "events": events, "count": len(events)}
