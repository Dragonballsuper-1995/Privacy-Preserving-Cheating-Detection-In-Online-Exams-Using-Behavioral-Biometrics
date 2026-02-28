import pytest
from app.utils.question_loader import QuestionLoader
from pathlib import Path

class TestQuestionLoader:
    def setup_method(self):
        self.loader = QuestionLoader("/dummy/path")

    def test_filter_questions(self):
        questions = [
            {"id": 1, "difficulty": "easy", "subject": "Math", "topic": "Algebra", "tags": ["basic"]},
            {"id": 2, "difficulty": "hard", "subject": "Math", "topic": "Calculus", "tags": ["advanced"]},
            {"id": 3, "difficulty": "easy", "subject": "Physics", "topic": "Mechanics", "tags": ["basic"]}
        ]
        
        # Difficulty filter
        res = self.loader.filter_questions(questions, difficulty="easy")
        assert len(res) == 2
        
        # Subject filter
        res = self.loader.filter_questions(questions, subject="Math")
        assert len(res) == 2
        
        # Topic filter
        res = self.loader.filter_questions(questions, topic="Calculus")
        assert len(res) == 1
        assert res[0]["id"] == 2
        
        # Tags filter
        res = self.loader.filter_questions(questions, tags=["advanced"])
        assert len(res) == 1
        
        # Multiple filters
        res = self.loader.filter_questions(questions, subject="Math", difficulty="easy")
        assert len(res) == 1
        assert res[0]["id"] == 1

    def test_validate_question_missing_fields(self):
        # Missing 'content'
        q = {"type": "mcq", "category": "mcq", "difficulty": "easy", "points": 1}
        is_valid, err = self.loader.validate_question(q)
        assert not is_valid
        assert "Missing required field" in err

    def test_validate_question_mcq(self):
        q = {
            "content": "What is 2+2?",
            "type": "mcq",
            "category": "mcq",
            "difficulty": "easy",
            "points": 1,
            "options": ["3", "4"],
            "correct_option": "4"
        }
        is_valid, err = self.loader.validate_question(q)
        assert is_valid
        assert err is None
        
        # Missing options
        q_bad = q.copy()
        del q_bad["options"]
        is_valid, err = self.loader.validate_question(q_bad)
        assert not is_valid

        # Too few options
        q_bad2 = q.copy()
        q_bad2["options"] = ["4"]
        is_valid, err = self.loader.validate_question(q_bad2)
        assert not is_valid

    def test_validate_question_coding(self):
        q = {
            "content": "Write a function...",
            "type": "coding",
            "category": "coding",
            "difficulty": "hard",
            "points": 10,
            "code_template": "def func(): pass",
            "test_cases": [{"input": "1", "output": "2"}]
        }
        is_valid, err = self.loader.validate_question(q)
        assert is_valid
        
        q_bad = q.copy()
        q_bad["test_cases"] = []
        is_valid, err = self.loader.validate_question(q_bad)
        assert not is_valid

    def test_validate_question_subjective(self):
        q = {
            "content": "Explain gravity.",
            "type": "subjective",
            "category": "subjective",
            "difficulty": "medium",
            "points": 5
        }
        is_valid, err = self.loader.validate_question(q)
        assert is_valid
