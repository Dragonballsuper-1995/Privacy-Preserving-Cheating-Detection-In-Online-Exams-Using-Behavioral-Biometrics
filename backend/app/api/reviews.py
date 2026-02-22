"""
Reviews API - Handles instructor feedback for flagged sessions.
Enables the "Human-in-the-loop" workflow.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.session import Session, ReviewStatus
from app.core.auth import require_admin, UserResponse

router = APIRouter()


class ReviewSubmission(BaseModel):
    """Payload for submitting an instructor review."""
    review_status: str  # 'confirmed_cheating' or 'false_positive'
    review_notes: Optional[str] = None


@router.post("/{session_id}")
def submit_session_review(
    session_id: str,
    submission: ReviewSubmission,
    db: DbSession = Depends(get_db),
    admin: UserResponse = Depends(require_admin)
):
    """Submit an instructor review for a specific session."""
    
    # Validate review status
    try:
        status_enum = ReviewStatus(submission.review_status)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid review_status. Must be one of: {[e.value for e in ReviewStatus if e != ReviewStatus.PENDING]}"
        )
        
    if status_enum == ReviewStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cannot manually set review to PENDING.")

    # Fetch session
    db_session = db.query(Session).filter(Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Update fields
    db_session.review_status = status_enum
    db_session.reviewed_by = admin.email
    db_session.review_notes = submission.review_notes
    db_session.reviewed_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_session)
    
    # Broadcast status update if WebSocket is active
    try:
        import asyncio
        from app.api.websocket import broadcast_session_status
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(broadcast_session_status(
                session_id,
                "review_submitted",
                {"review_status": status_enum.value}
            ))
    except Exception as e:
        print(f"WS Broadcast failed for review: {e}")
        pass
        
    return {
        "success": True, 
        "session_id": session_id, 
        "review_status": status_enum.value
    }
