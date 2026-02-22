"""
Sessions API - Manages exam sessions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
import uuid

router = APIRouter()


class SessionStatus(str, Enum):
    """Exam session status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    ANALYZED = "analyzed"


class CreateSessionRequest(BaseModel):
    """Request to create a new exam session."""
    exam_id: str
    student_id: str


class SessionResponse(BaseModel):
    """Session data response."""
    id: str
    exam_id: str
    student_id: str
    status: SessionStatus
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    current_question: int = 0


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer."""
    question_id: str
    content: str


# In-memory storage (will be replaced with database)
sessions_db: dict = {}


@router.post("/create", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new exam session."""
    session_id = str(uuid.uuid4())
    
    session = SessionResponse(
        id=session_id,
        exam_id=request.exam_id,
        student_id=request.student_id,
        status=SessionStatus.NOT_STARTED,
        current_question=0
    )
    
    sessions_db[session_id] = session.model_dump()
    return session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(**sessions_db[session_id])


@router.post("/{session_id}/start")
async def start_session(session_id: str):
    """Start an exam session."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions_db[session_id]["status"] = SessionStatus.IN_PROGRESS
    sessions_db[session_id]["started_at"] = datetime.now(timezone.utc).isoformat()
    
    return {"message": "Session started", "session_id": session_id}


@router.post("/{session_id}/submit")
async def submit_session(session_id: str):
    """Submit the exam session."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions_db[session_id]["status"] = SessionStatus.SUBMITTED
    sessions_db[session_id]["submitted_at"] = datetime.now(timezone.utc).isoformat()
    
    return {"message": "Exam submitted successfully", "session_id": session_id}


@router.post("/{session_id}/answer")
async def submit_answer(session_id: str, answer: SubmitAnswerRequest):
    """Submit an answer for a question."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Store answer (in-memory for now)
    if "answers" not in sessions_db[session_id]:
        sessions_db[session_id]["answers"] = {}
    
    sessions_db[session_id]["answers"][answer.question_id] = {
        "content": answer.content,
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }
    
    return {"message": "Answer saved", "question_id": answer.question_id}


@router.get("/list/all")
async def list_sessions(status: Optional[SessionStatus] = None):
    """List all sessions, optionally filtered by status."""
    sessions = list(sessions_db.values())
    
    if status:
        sessions = [s for s in sessions if s["status"] == status]
    
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/{session_id}/result")
async def get_session_result(session_id: str):
    """
    Get session result for the student.

    Returns submission details and answers without exposing
    risk score or analysis data (those are admin-only).
    """
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions_db[session_id]
    answers_raw = session.get("answers", {})

    # Build answer summary (question_id → truncated content + timestamp)
    answers_summary = []
    for qid, ans in answers_raw.items():
        content = ans.get("content", "") if isinstance(ans, dict) else str(ans)
        submitted_at = ans.get("submitted_at") if isinstance(ans, dict) else None
        answers_summary.append({
            "question_id": qid,
            "answered": bool(content.strip()),
            "length": len(content),
            "submitted_at": submitted_at,
        })

    return {
        "session_id": session_id,
        "exam_id": session.get("exam_id", ""),
        "status": session.get("status", "submitted"),
        "started_at": session.get("started_at"),
        "submitted_at": session.get("submitted_at"),
        "answers": answers_summary,
        "total_answered": sum(1 for a in answers_summary if a["answered"]),
        "total_questions": len(answers_summary),
    }
