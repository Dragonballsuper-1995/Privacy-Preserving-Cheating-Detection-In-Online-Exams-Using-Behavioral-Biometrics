"""
Feature Extraction Pipeline

Unified pipeline that extracts all behavioral features from session events
and computes a combined risk score.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json
import os

from app.features.keystroke import (
    extract_keystroke_features, 
    calculate_anomaly_score as keystroke_anomaly_score,
    KeystrokeFeatures
)
from app.features.hesitation import (
    extract_hesitation_features,
    calculate_hesitation_score,
    HesitationFeatures
)
from app.features.paste import (
    extract_paste_features,
    calculate_paste_score,
    PasteFeatures
)
from app.features.focus import (
    extract_focus_features,
    calculate_focus_score,
    FocusFeatures
)
from app.core.config import settings


@dataclass
class SessionFeatures:
    """Complete feature set for a session."""
    session_id: str
    question_id: Optional[str] = None
    
    # Individual feature groups
    keystroke: KeystrokeFeatures = field(default_factory=KeystrokeFeatures)
    hesitation: HesitationFeatures = field(default_factory=HesitationFeatures)
    paste: PasteFeatures = field(default_factory=PasteFeatures)
    focus: FocusFeatures = field(default_factory=FocusFeatures)
    
    # Individual scores
    typing_score: float = 0.0
    hesitation_score: float = 0.0
    paste_score: float = 0.0
    focus_score: float = 0.0
    
    # Combined score
    overall_score: float = 0.0
    is_flagged: bool = False
    flag_reasons: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "question_id": self.question_id,
            "keystroke": self.keystroke.to_dict(),
            "hesitation": self.hesitation.to_dict(),
            "paste": self.paste.to_dict(),
            "focus": self.focus.to_dict(),
            "typing_score": self.typing_score,
            "hesitation_score": self.hesitation_score,
            "paste_score": self.paste_score,
            "focus_score": self.focus_score,
            "overall_score": self.overall_score,
            "is_flagged": self.is_flagged,
            "flag_reasons": self.flag_reasons,
        }


class FeatureExtractor:
    """
    Main feature extraction class.
    
    Orchestrates the extraction of all feature types from session events
    and computes the combined risk score.
    """
    
    # Risk score weights (based on research and tuning)
    WEIGHTS = {
        "typing": 0.25,
        "hesitation": 0.25,
        "paste": 0.30,
        "focus": 0.20,
    }
    
    def __init__(
        self,
        pause_threshold_ms: float = 2000,
        risk_threshold: float = 0.75
    ):
        """
        Initialize the feature extractor.
        
        Args:
            pause_threshold_ms: Minimum pause duration to consider
            risk_threshold: Score threshold for flagging
        """
        self.pause_threshold_ms = pause_threshold_ms
        self.risk_threshold = risk_threshold
    
    def extract_features(
        self, 
        events: List[Dict[str, Any]], 
        session_id: str,
        question_id: Optional[str] = None
    ) -> SessionFeatures:
        """
        Extract all features from a list of events.
        
        Args:
            events: List of behavior event dictionaries
            session_id: Session identifier
            question_id: Optional question identifier
            
        Returns:
            SessionFeatures with all extracted features and scores
        """
        features = SessionFeatures(
            session_id=session_id,
            question_id=question_id
        )
        
        if not events:
            return features
        
        # Extract individual feature sets
        features.keystroke = extract_keystroke_features(events)
        features.hesitation = extract_hesitation_features(events, self.pause_threshold_ms)
        features.paste = extract_paste_features(events)
        features.focus = extract_focus_features(events)
        
        # Calculate individual scores
        features.typing_score = keystroke_anomaly_score(features.keystroke)
        features.hesitation_score = calculate_hesitation_score(features.hesitation)
        features.paste_score = calculate_paste_score(features.paste)
        features.focus_score = calculate_focus_score(features.focus)
        
        # Calculate weighted overall score
        features.overall_score = (
            self.WEIGHTS["typing"] * features.typing_score +
            self.WEIGHTS["hesitation"] * features.hesitation_score +
            self.WEIGHTS["paste"] * features.paste_score +
            self.WEIGHTS["focus"] * features.focus_score
        )
        
        # Determine if flagged
        features.is_flagged = features.overall_score >= self.risk_threshold
        
        # Generate flag reasons
        features.flag_reasons = self._generate_flag_reasons(features)
        
        return features
    
    def _generate_flag_reasons(self, features: SessionFeatures) -> List[str]:
        """Generate human-readable reasons for flags."""
        reasons = []
        
        # Typing anomalies
        if features.typing_score >= 0.3:
            if features.keystroke.typing_speed_wpm > 120:
                reasons.append(f"Unusually fast typing: {features.keystroke.typing_speed_wpm:.0f} WPM")
            if features.keystroke.std_inter_key_delay > 500:
                reasons.append("Erratic typing rhythm detected")
        
        # Hesitation concerns
        if features.hesitation_score >= 0.3:
            if features.hesitation.long_pauses >= 1:
                reasons.append(f"Long pauses detected: {features.hesitation.long_pauses} pauses > 15s")
            if features.hesitation.max_pause_duration > 30000:
                reasons.append(f"Extended pause: {features.hesitation.max_pause_duration/1000:.1f}s")
        
        # Paste behavior
        if features.paste_score >= 0.3:
            if features.paste.paste_count > 0:
                reasons.append(f"Content pasted: {features.paste.paste_count} paste events")
            if features.paste.large_paste_count > 0:
                reasons.append(f"Large paste detected: {features.paste.total_paste_length} chars total")
            if features.paste.paste_after_blur > 0:
                reasons.append(f"Paste after tab switch: {features.paste.paste_after_blur} times")
        
        # Focus/tab switching
        if features.focus_score >= 0.3:
            if features.focus.blur_count >= 3:
                reasons.append(f"Tab switching detected: {features.focus.blur_count} times")
            if features.focus.extended_absences >= 1:
                reasons.append(f"Extended absence: {features.focus.extended_absences} periods > 30s")
        
        return reasons
    
    def extract_from_file(self, session_id: str) -> SessionFeatures:
        """
        Extract features from a session's JSONL log file.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionFeatures with all extracted features
        """
        log_file = os.path.join(settings.event_logs_dir, f"session_{session_id}.jsonl")
        
        if not os.path.exists(log_file):
            return SessionFeatures(session_id=session_id)
        
        events = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return self.extract_features(events, session_id)


def extract_all_features(
    events: List[Dict[str, Any]], 
    session_id: str,
    question_id: Optional[str] = None
) -> SessionFeatures:
    """
    Convenience function to extract all features.
    
    Args:
        events: List of behavior events
        session_id: Session identifier
        question_id: Optional question identifier
        
    Returns:
        SessionFeatures with all extracted features and scores
    """
    extractor = FeatureExtractor(
        pause_threshold_ms=settings.min_pause_duration,
        risk_threshold=settings.risk_threshold
    )
    return extractor.extract_features(events, session_id, question_id)


def extract_features_by_question(
    events: List[Dict[str, Any]], 
    session_id: str
) -> Dict[str, SessionFeatures]:
    """
    Extract features grouped by question.
    
    Args:
        events: List of all session events
        session_id: Session identifier
        
    Returns:
        Dictionary mapping question_id to SessionFeatures
    """
    # Group events by question
    events_by_question: Dict[str, List[Dict]] = {}
    
    for event in events:
        question_id = event.get("question_id", "unknown")
        if question_id not in events_by_question:
            events_by_question[question_id] = []
        events_by_question[question_id].append(event)
    
    # Extract features for each question
    results = {}
    extractor = FeatureExtractor(
        pause_threshold_ms=settings.min_pause_duration,
        risk_threshold=settings.risk_threshold
    )
    
    for question_id, question_events in events_by_question.items():
        results[question_id] = extractor.extract_features(
            question_events, session_id, question_id
        )
    
    return results
