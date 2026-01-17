"""
Exams API - Manages exam content and questions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import uuid

router = APIRouter()


class QuestionType(str, Enum):
    """Types of exam questions."""
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    CODING = "coding"


class MCQOption(BaseModel):
    """MCQ option."""
    id: str
    text: str


class Question(BaseModel):
    """Exam question model."""
    id: str
    type: QuestionType
    content: str
    points: int = 10
    
    # MCQ specific
    options: Optional[List[MCQOption]] = None
    correct_option: Optional[str] = None
    
    # Coding specific
    code_template: Optional[str] = None
    language: Optional[str] = None
    test_cases: Optional[List[dict]] = None


class Exam(BaseModel):
    """Exam model."""
    id: str
    title: str
    description: str
    duration_minutes: int
    questions: List[Question]


class CreateExamRequest(BaseModel):
    """Request to create an exam."""
    title: str
    description: str
    duration_minutes: int


# Mock exam data for development
MOCK_EXAMS: dict = {
    "demo-exam-1": Exam(
        id="demo-exam-1",
        title="Python Fundamentals Assessment",
        description="Test your knowledge of Python basics including data types, control flow, and functions.",
        duration_minutes=30,
        questions=[
            Question(
                id="q1",
                type=QuestionType.MCQ,
                content="What is the output of: print(type([]))?",
                points=5,
                options=[
                    MCQOption(id="a", text="<class 'tuple'>"),
                    MCQOption(id="b", text="<class 'list'>"),
                    MCQOption(id="c", text="<class 'dict'>"),
                    MCQOption(id="d", text="<class 'set'>"),
                ],
                correct_option="b"
            ),
            Question(
                id="q2",
                type=QuestionType.MCQ,
                content="Which keyword is used to define a function in Python?",
                points=5,
                options=[
                    MCQOption(id="a", text="function"),
                    MCQOption(id="b", text="func"),
                    MCQOption(id="c", text="def"),
                    MCQOption(id="d", text="define"),
                ],
                correct_option="c"
            ),
            Question(
                id="q3",
                type=QuestionType.SHORT_ANSWER,
                content="Explain the difference between a list and a tuple in Python. When would you use each?",
                points=15
            ),
            Question(
                id="q4",
                type=QuestionType.SHORT_ANSWER,
                content="What is a Python decorator? Provide a simple example of when you might use one.",
                points=15
            ),
            Question(
                id="q5",
                type=QuestionType.CODING,
                content="Write a function called `is_palindrome` that takes a string and returns True if it's a palindrome, False otherwise. Ignore case and spaces.",
                points=25,
                language="python",
                code_template='''def is_palindrome(s: str) -> bool:
    """
    Check if a string is a palindrome.
    Ignore case and spaces.
    
    Examples:
        is_palindrome("racecar") -> True
        is_palindrome("hello") -> False
        is_palindrome("A man a plan a canal Panama") -> True
    """
    # Your code here
    pass
''',
                test_cases=[
                    {"input": "racecar", "expected": True},
                    {"input": "hello", "expected": False},
                    {"input": "A man a plan a canal Panama", "expected": True},
                    {"input": "Was it a car or a cat I saw", "expected": True},
                    {"input": "No lemon no melon", "expected": True},
                ]
            ),
            Question(
                id="q6",
                type=QuestionType.CODING,
                content="Write a function called `two_sum` that takes a list of integers and a target sum. Return the indices of the two numbers that add up to the target.",
                points=25,
                language="python",
                code_template='''def two_sum(nums: list, target: int) -> list:
    """
    Find two numbers in the list that add up to target.
    Return their indices.
    
    Examples:
        two_sum([2, 7, 11, 15], 9) -> [0, 1]
        two_sum([3, 2, 4], 6) -> [1, 2]
    """
    # Your code here
    pass
''',
                test_cases=[
                    {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
                    {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
                    {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
                ]
            ),
        ]
    )
}

# Custom exams storage
exams_db: dict = {}


@router.get("/list")
async def list_exams():
    """List all available exams."""
    all_exams = {**MOCK_EXAMS, **exams_db}
    return {
        "exams": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "duration_minutes": e.duration_minutes,
                "question_count": len(e.questions)
            }
            for e in all_exams.values()
        ]
    }


@router.get("/{exam_id}")
async def get_exam(exam_id: str, include_answers: bool = False):
    """Get exam details with questions."""
    all_exams = {**MOCK_EXAMS, **exams_db}
    
    if exam_id not in all_exams:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exam = all_exams[exam_id]
    
    # Remove correct answers if not requested
    if not include_answers:
        exam_dict = exam.model_dump()
        for q in exam_dict["questions"]:
            if q.get("correct_option"):
                del q["correct_option"]
        return exam_dict
    
    return exam


@router.post("/create")
async def create_exam(request: CreateExamRequest):
    """Create a new exam."""
    exam_id = str(uuid.uuid4())
    
    exam = Exam(
        id=exam_id,
        title=request.title,
        description=request.description,
        duration_minutes=request.duration_minutes,
        questions=[]
    )
    
    exams_db[exam_id] = exam
    return {"message": "Exam created", "exam_id": exam_id}


@router.post("/{exam_id}/questions")
async def add_question(exam_id: str, question: Question):
    """Add a question to an exam."""
    if exam_id not in exams_db:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exams_db[exam_id].questions.append(question)
    return {"message": "Question added", "question_id": question.id}
