"""
Session and Answer models
"""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.core.database import Base


class SessionStatus(str, enum.Enum):
    """Status of an exam session."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    ANALYZED = "analyzed"


class ReviewStatus(str, enum.Enum):
    """Status of instructor review for flagged sessions."""
    PENDING = "pending"
    CONFIRMED_CHEATING = "confirmed_cheating"
    FALSE_POSITIVE = "false_positive"


class Session(Base):
    """Session model - represents a student's exam attempt."""
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String(36), ForeignKey("exams.id"), nullable=False)
    student_id = Column(String(100), nullable=False)
    status = Column(Enum(SessionStatus, native_enum=False), default=SessionStatus.NOT_STARTED)
    started_at = Column(DateTime)
    submitted_at = Column(DateTime)
    # Review Fields
    review_status = Column(Enum(ReviewStatus, native_enum=False), default=ReviewStatus.PENDING)
    reviewed_by = Column(String(100), nullable=True) # Instructor ID
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exam = relationship("Exam", back_populates="sessions")
    answers = relationship("Answer", back_populates="session", cascade="all, delete-orphan")
    risk_scores = relationship("RiskScore", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "student_id": self.student_id,
            "status": self.status.value if self.status else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "review_status": self.review_status.value if self.review_status else None,
            "reviewed_by": self.reviewed_by,
            "review_notes": self.review_notes,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Answer(Base):
    """Answer model - represents a student's answer to a question."""
    __tablename__ = "answers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    content = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="answers")
    question = relationship("Question", back_populates="answers")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question_id": self.question_id,
            "content": self.content,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }
