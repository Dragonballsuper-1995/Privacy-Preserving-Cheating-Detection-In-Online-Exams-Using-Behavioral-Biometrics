"""
Behavior Event, Feature Vector, and Risk Score models
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class BehaviorEvent(Base):
    """Raw behavior event from frontend logging."""
    __tablename__ = "behavior_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    question_id = Column(String(36))
    event_type = Column(String(50), nullable=False)  # key, paste, focus
    data = Column(JSON)
    timestamp = Column(Float, nullable=False)  # Client timestamp in ms
    logged_at = Column(DateTime, default=datetime.utcnow)


class FeatureVector(Base):
    """Extracted features from behavior events."""
    __tablename__ = "feature_vectors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    question_id = Column(String(36))
    
    # Keystroke dynamics
    mean_inter_key_delay = Column(Float, default=0.0)
    std_inter_key_delay = Column(Float, default=0.0)
    typing_speed_wpm = Column(Float, default=0.0)
    
    # Hesitation
    pause_count = Column(Integer, default=0)
    max_pause_duration = Column(Float, default=0.0)
    total_idle_time = Column(Float, default=0.0)
    
    # Paste behavior
    paste_count = Column(Integer, default=0)
    total_paste_length = Column(Integer, default=0)
    
    # Edit patterns
    backspace_count = Column(Integer, default=0)
    backspace_ratio = Column(Float, default=0.0)
    
    # Focus events
    blur_count = Column(Integer, default=0)
    total_unfocused_time = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "question_id": self.question_id,
            "mean_inter_key_delay": self.mean_inter_key_delay,
            "std_inter_key_delay": self.std_inter_key_delay,
            "typing_speed_wpm": self.typing_speed_wpm,
            "pause_count": self.pause_count,
            "max_pause_duration": self.max_pause_duration,
            "total_idle_time": self.total_idle_time,
            "paste_count": self.paste_count,
            "total_paste_length": self.total_paste_length,
            "backspace_count": self.backspace_count,
            "backspace_ratio": self.backspace_ratio,
            "blur_count": self.blur_count,
            "total_unfocused_time": self.total_unfocused_time,
        }


class RiskScore(Base):
    """Risk assessment for a session."""
    __tablename__ = "risk_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    
    overall_score = Column(Float, default=0.0)
    typing_score = Column(Float, default=0.0)
    hesitation_score = Column(Float, default=0.0)
    similarity_score = Column(Float, default=0.0)
    editing_score = Column(Float, default=0.0)
    
    is_flagged = Column(Boolean, default=False)
    flag_reasons = Column(JSON)  # List of reason strings
    
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="risk_scores")

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "overall_score": self.overall_score,
            "typing_score": self.typing_score,
            "hesitation_score": self.hesitation_score,
            "similarity_score": self.similarity_score,
            "editing_score": self.editing_score,
            "is_flagged": self.is_flagged,
            "flag_reasons": self.flag_reasons or [],
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
        }
