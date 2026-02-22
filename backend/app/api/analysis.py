"""
Analysis API - Feature extraction and risk scoring.
Uses the new modular feature extraction pipeline.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import os
from app.core.config import settings
from app.core.auth import require_instructor, UserResponse
from app.core.database import get_db
from app.models.session import Session as DbSession
from sqlalchemy.orm import Session as SQLAlchemySession
from app.features.pipeline import (
    FeatureExtractor, 
    extract_all_features,
    extract_features_by_question,
    SessionFeatures
)

router = APIRouter()


class FeatureVectorResponse(BaseModel):
    """Feature vector response."""
    session_id: str
    question_id: Optional[str] = None
    
    # Keystroke features
    mean_inter_key_delay: float = 0.0
    std_inter_key_delay: float = 0.0
    typing_speed_wpm: float = 0.0
    
    # Hesitation features
    pause_count: int = 0
    max_pause_duration: float = 0.0
    total_idle_time: float = 0.0
    
    # Paste features
    paste_count: int = 0
    total_paste_length: int = 0
    
    # Focus features
    blur_count: int = 0
    total_unfocused_time: float = 0.0


class RiskScoreResponse(BaseModel):
    """Risk assessment response."""
    session_id: str
    overall_score: float
    typing_score: float
    hesitation_score: float
    paste_score: float
    focus_score: float
    similarity_score: float = 0.0  # AI detection + web source check
    
    is_flagged: bool
    flag_reasons: List[str]
    
    # Optional detailed features
    features: Optional[Dict] = None


class AnalysisRequest(BaseModel):
    """Request to analyze a session."""
    session_id: str
    include_features: bool = True
    by_question: bool = False


def session_features_to_response(features: SessionFeatures, include_details: bool = True) -> RiskScoreResponse:
    """Convert SessionFeatures to API response."""
    response = RiskScoreResponse(
        session_id=features.session_id,
        overall_score=features.overall_score,
        typing_score=features.typing_score,
        hesitation_score=features.hesitation_score,
        paste_score=features.paste_score,
        focus_score=features.focus_score,
        similarity_score=features.similarity_score,
        is_flagged=features.is_flagged,
        flag_reasons=features.flag_reasons,
    )
    
    if include_details:
        response.features = {
            "keystroke": features.keystroke.to_dict(),
            "hesitation": features.hesitation.to_dict(),
            "paste": features.paste.to_dict(),
            "focus": features.focus.to_dict(),
            "similarity": features.similarity.to_dict(),
        }
    
    return response


def load_session_events(session_id: str) -> List[Dict]:
    """Load events from session log file."""
    log_file = os.path.join(settings.event_logs_dir, f"session_{session_id}.jsonl")
    
    if not os.path.exists(log_file):
        return []
    
    events = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    return events


@router.post("/analyze", response_model=RiskScoreResponse)
async def analyze_session(request: AnalysisRequest, user: UserResponse = Depends(require_instructor)):
    """
    Analyze a session and compute risk score.
    
    Uses the modular feature extraction pipeline to extract:
    - Keystroke dynamics
    - Hesitation patterns  
    - Paste behavior
    - Focus/blur patterns
    
    Returns a combined risk score with flag reasons.
    """
    events = load_session_events(request.session_id)
    
    if not events:
        raise HTTPException(status_code=404, detail="Session events not found")
    
    # Extract features using the pipeline
    features = extract_all_features(events, request.session_id)
    
    return session_features_to_response(features, request.include_features)


@router.post("/analyze/questions")
async def analyze_by_question(request: AnalysisRequest, user: UserResponse = Depends(require_instructor)):
    """
    Analyze a session with per-question breakdown.
    
    Returns risk scores for each question separately.
    """
    events = load_session_events(request.session_id)
    
    if not events:
        raise HTTPException(status_code=404, detail="Session events not found")
    
    # Extract features per question
    features_by_question = extract_features_by_question(events, request.session_id)
    
    results = {}
    for question_id, features in features_by_question.items():
        results[question_id] = session_features_to_response(
            features, request.include_features
        ).model_dump()
    
    return {
        "session_id": request.session_id,
        "questions": results,
        "question_count": len(results)
    }


@router.get("/session/{session_id}/features")
async def get_session_features(session_id: str, user: UserResponse = Depends(require_instructor)):
    """Get detailed extracted features for a session."""
    events = load_session_events(session_id)
    
    if not events:
        raise HTTPException(status_code=404, detail="Session not found")
    
    features = extract_all_features(events, session_id)
    
    return features.to_dict()


@router.get("/session/{session_id}/timeline")
async def get_session_timeline(session_id: str, limit: int = 100, user: UserResponse = Depends(require_instructor)):
    """
    Get a timeline of events for visualization.
    
    Returns events with extracted feature annotations.
    """
    events = load_session_events(session_id)
    
    if not events:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Sort and limit
    sorted_events = sorted(events, key=lambda x: x.get("timestamp", 0))[:limit]
    
    # Add annotations
    timeline = []
    for event in sorted_events:
        entry = {
            "timestamp": event.get("timestamp"),
            "type": event.get("event_type"),
            "data": event.get("data", {}),
            "question_id": event.get("question_id"),
        }
        
        # Add annotations for significant events
        if event.get("event_type") == "paste":
            entry["annotation"] = "paste_event"
            entry["severity"] = "high"
        elif event.get("event_type") == "focus":
            if event.get("data", {}).get("type") == "blur":
                entry["annotation"] = "tab_switch"
                entry["severity"] = "medium"
        
        timeline.append(entry)
    
    return {
        "session_id": session_id,
        "timeline": timeline,
        "event_count": len(timeline)
    }



@router.get("/dashboard/summary")
async def get_dashboard_summary(
    user: UserResponse = Depends(require_instructor),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Get summary statistics for all analyzed sessions.
    Returns aggregated data and list of all sessions with risk scores.
    
    RISK SCORING FORMULA:
    final_risk = (behavioral * 0.35) + (anomaly * 0.35) + (similarity * 0.30)
    
    Where:
    - behavioral = average of (typing, hesitation, paste, focus) scores
    - anomaly = Isolation Forest anomaly detection score
    - similarity = Answer similarity score (if available)
    """
    log_dir = settings.event_logs_dir
    
    if not os.path.exists(log_dir):
        return {"total_sessions": 0, "flagged_sessions": 0, "sessions": []}
    
    sessions = []
    flagged_count = 0
    
    extractor = FeatureExtractor(
        pause_threshold_ms=settings.min_pause_duration,
        risk_threshold=settings.risk_threshold
    )
    
    # Pre-fetch all session database records to avoid N+1 queries for review status
    db_sessions = db.query(DbSession.id, DbSession.review_status).all()
    review_status_map = {row.id: row.review_status.value if row.review_status else "pending" for row in db_sessions}
    
    for filename in os.listdir(log_dir):
        if filename.startswith("session_") and filename.endswith(".jsonl"):
            session_id = filename.replace("session_", "").replace(".jsonl", "")
            filepath = os.path.join(log_dir, filename)
            # Check for cached result
            result_file = os.path.join(log_dir, f"session_{session_id}.result.json")
            cached_data = None
            
            try:
                log_mtime = os.path.getmtime(filepath)
                if os.path.exists(result_file):
                    result_mtime = os.path.getmtime(result_file)
                    if result_mtime >= log_mtime:
                        with open(result_file, 'r') as f:
                            cached_data = json.load(f)
            except Exception as e:
                # Ignore cache errors and re-process
                pass
            
            if cached_data:
                # Invalidate cache if it doesn't have similarity_score (old format)
                if "scores" in cached_data and "similarity" not in cached_data["scores"]:
                    cached_data = None  # Force re-analysis
                else:
                    if cached_data.get("is_flagged"):
                        flagged_count += 1
                    # Override review_status with real DB state, as cache can't track instructor DB action
                    cached_data["review_status"] = review_status_map.get(session_id, "pending")
                    sessions.append(cached_data)
                    continue
            
            # Cache miss - Process from scratch
            metadata_file = os.path.join(log_dir, f"session_{session_id}.meta.json")
            
            # Get file modification time as created_at
            try:
                created_at = datetime.fromtimestamp(log_mtime).isoformat()
            except:
                created_at = None
            
            # Check if this is a simulated session by looking for metadata file
            is_simulated = False
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as mf:
                        metadata = json.load(mf)
                        is_simulated = metadata.get('is_simulated', False)
                except:
                    pass
            
            # Fallback: check session_id pattern
            if not is_simulated:
                is_simulated = (
                    session_id.startswith('sim-') or 
                    session_id.startswith('test-')
                )
            
            # Load and analyze
            events = load_session_events(session_id)
            
            if events:
                features = extractor.extract_features(events, session_id)
                
                if features.is_flagged:
                    flagged_count += 1
                
                session_data = {
                    "session_id": session_id,
                    "risk_score": features.overall_score,
                    "is_flagged": features.is_flagged,
                    "event_count": len(events),
                    "flag_reasons": features.flag_reasons[:3],  # Top 3 reasons
                    "created_at": created_at,  # Added timestamp
                    "is_simulated": is_simulated,  # Use the value determined from metadata
                    "review_status": review_status_map.get(session_id, "pending"),
                    "scores": {
                        "typing": features.typing_score,
                        "hesitation": features.hesitation_score,
                        "paste": features.paste_score,
                        "focus": features.focus_score,
                        "similarity": features.similarity_score,
                    }
                }
                
                # Save to cache
                try:
                    with open(result_file, 'w') as f:
                        json.dump(session_data, f)
                except:
                    pass
                
                sessions.append(session_data)
    
    # Sort by created_at (most recent first), then by risk score
    sessions.sort(key=lambda x: (
        x.get("created_at") or "0",  # Put sessions without timestamps last
        -x["risk_score"]
    ), reverse=True)
    
    return {
        "total_sessions": len(sessions),
        "flagged_sessions": flagged_count,
        "sessions": sessions
    }


@router.get("/export/csv")
async def export_sessions_csv(user: UserResponse = Depends(require_instructor)):
    """
    Export all session analysis data as a CSV file.

    Streams a CSV with columns:
    session_id, risk_score, is_flagged, event_count, typing, hesitation,
    paste, focus, flag_reasons, created_at, is_simulated
    """
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse

    log_dir = settings.event_logs_dir
    rows: list[dict] = []

    if os.path.exists(log_dir):
        extractor = FeatureExtractor(
            pause_threshold_ms=settings.min_pause_duration,
            risk_threshold=settings.risk_threshold,
        )

        for filename in os.listdir(log_dir):
            if not (filename.startswith("session_") and filename.endswith(".jsonl")):
                continue

            session_id = filename.replace("session_", "").replace(".jsonl", "")
            filepath = os.path.join(log_dir, filename)

            # Try cache first
            result_file = os.path.join(log_dir, f"session_{session_id}.result.json")
            cached = None
            try:
                log_mtime = os.path.getmtime(filepath)
                if os.path.exists(result_file):
                    if os.path.getmtime(result_file) >= log_mtime:
                        with open(result_file, "r") as f:
                            cached = json.load(f)
            except Exception:
                pass

            if cached:
                rows.append(cached)
                continue

            # Compute from scratch
            events = load_session_events(session_id)
            if events:
                features = extractor.extract_features(events, session_id)
                try:
                    created_at = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                except Exception:
                    created_at = None

                rows.append({
                    "session_id": session_id,
                    "risk_score": features.overall_score,
                    "is_flagged": features.is_flagged,
                    "event_count": len(events),
                    "flag_reasons": features.flag_reasons[:3],
                    "created_at": created_at,
                    "is_simulated": session_id.startswith("sim-") or session_id.startswith("test-"),
                    "scores": {
                        "typing": features.typing_score,
                        "hesitation": features.hesitation_score,
                        "paste": features.paste_score,
                        "focus": features.focus_score,
                        "similarity": features.similarity_score,
                    },
                })

    # Build CSV
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "session_id", "risk_score", "is_flagged", "event_count",
        "typing_score", "hesitation_score", "paste_score", "focus_score",
        "similarity_score",
        "flag_reasons", "created_at", "is_simulated",
    ])
    for r in rows:
        scores = r.get("scores", {})
        writer.writerow([
            r.get("session_id", ""),
            round(r.get("risk_score", 0), 4),
            r.get("is_flagged", False),
            r.get("event_count", 0),
            round(scores.get("typing", 0), 4),
            round(scores.get("hesitation", 0), 4),
            round(scores.get("paste", 0), 4),
            round(scores.get("focus", 0), 4),
            round(scores.get("similarity", 0), 4),
            "; ".join(r.get("flag_reasons", [])),
            r.get("created_at", ""),
            r.get("is_simulated", False),
        ])

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sessions_export.csv"},
    )

