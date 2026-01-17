"""
Exam and Question models
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.core.database import Base


class QuestionType(str, enum.Enum):
    """Types of exam questions."""
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    CODING = "coding"


class Exam(Base):
    """Exam model - represents an exam/assessment."""
    __tablename__ = "exams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, default=60)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="exam")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "question_count": len(self.questions) if self.questions else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Question(Base):
    """Question model - represents a single question in an exam."""
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String(36), ForeignKey("exams.id"), nullable=False)
    type = Column(Enum(QuestionType), nullable=False)
    content = Column(Text, nullable=False)
    points = Column(Integer, default=10)
    order = Column(Integer, default=0)
    
    # MCQ specific
    options = Column(JSON)  # List of {id, text}
    correct_option = Column(String(10))
    
    # Coding specific
    code_template = Column(Text)
    language = Column(String(50), default="python")
    test_cases = Column(JSON)  # List of {input, expected}

    # Relationships
    exam = relationship("Exam", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

    def to_dict(self, include_answer: bool = False):
        result = {
            "id": self.id,
            "type": self.type.value if self.type else None,
            "content": self.content,
            "points": self.points,
            "options": self.options,
            "code_template": self.code_template,
            "language": self.language,
            "test_cases": self.test_cases,
        }
        if include_answer:
            result["correct_option"] = self.correct_option
        return result
