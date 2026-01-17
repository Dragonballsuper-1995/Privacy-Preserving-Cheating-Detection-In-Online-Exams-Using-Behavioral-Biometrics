"""
Analysis API - Feature extraction and risk scoring.
Uses the new modular feature extraction pipeline.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os

from app.core.config import settings
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
    paste_score: float  # Renamed from similarity to paste
    focus_score: float  # Renamed from editing to focus
    
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
        is_flagged=features.is_flagged,
        flag_reasons=features.flag_reasons,
    )
    
    if include_details:
        response.features = {
            "keystroke": features.keystroke.to_dict(),
            "hesitation": features.hesitation.to_dict(),
            "paste": features.paste.to_dict(),
            "focus": features.focus.to_dict(),
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
async def analyze_session(request: AnalysisRequest):
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
async def analyze_by_question(request: AnalysisRequest):
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
async def get_session_features(session_id: str):
    """Get detailed extracted features for a session."""
    events = load_session_events(session_id)
    
    if not events:
        raise HTTPException(status_code=404, detail="Session not found")
    
    features = extract_all_features(events, session_id)
    
    return features.to_dict()


@router.get("/session/{session_id}/timeline")
async def get_session_timeline(session_id: str, limit: int = 100):
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
async def get_dashboard_summary():
    """Get summary statistics for the admin dashboard."""
    log_dir = settings.event_logs_dir
    
    if not os.path.exists(log_dir):
        return {"total_sessions": 0, "flagged_sessions": 0, "sessions": []}
    
    sessions = []
    flagged_count = 0
    
    extractor = FeatureExtractor(
        pause_threshold_ms=settings.min_pause_duration,
        risk_threshold=settings.risk_threshold
    )
    
    for filename in os.listdir(log_dir):
        if filename.startswith("session_") and filename.endswith(".jsonl"):
            session_id = filename.replace("session_", "").replace(".jsonl", "")
            
            # Load and analyze
            events = load_session_events(session_id)
            
            if events:
                features = extractor.extract_features(events, session_id)
                
                if features.is_flagged:
                    flagged_count += 1
                
                sessions.append({
                    "session_id": session_id,
                    "risk_score": features.overall_score,
                    "is_flagged": features.is_flagged,
                    "event_count": len(events),
                    "flag_reasons": features.flag_reasons[:3],  # Top 3 reasons
                    "scores": {
                        "typing": features.typing_score,
                        "hesitation": features.hesitation_score,
                        "paste": features.paste_score,
                        "focus": features.focus_score,
                    }
                })
    
    # Sort by risk score (highest first)
    sessions.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return {
        "total_sessions": len(sessions),
        "flagged_sessions": flagged_count,
        "sessions": sessions
    }
