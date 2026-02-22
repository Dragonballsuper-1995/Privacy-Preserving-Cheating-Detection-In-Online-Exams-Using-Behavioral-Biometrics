"""
Exams API - Manages exam content and questions.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import uuid

from app.utils.question_loader import QuestionLoader

router = APIRouter()


class QuestionType(str, Enum):
    """Types of exam questions."""
    MCQ = "mcq"
    SUBJECTIVE = "subjective"
    CODING = "coding"


class Difficulty(str, Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


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
    
    # New metadata
    category: Optional[QuestionType] = None
    difficulty: Optional[Difficulty] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    explanation: Optional[str] = None
    
    # MCQ specific
    options: Optional[List[MCQOption]] = None
    correct_option: Optional[str] = None
    
    # Coding specific
    code_template: Optional[str] = None
    language: Optional[str] = None
    test_cases: Optional[List[dict]] = None
    
    # Subjective specific
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    rubric: Optional[dict] = None


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
                category=QuestionType.MCQ,
                difficulty=Difficulty.EASY,
                subject="Python Programming",
                topic="Data Types",
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
                category=QuestionType.MCQ,
                difficulty=Difficulty.EASY,
                subject="Python Programming",
                topic="Functions",
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
                type=QuestionType.SUBJECTIVE,
                category=QuestionType.SUBJECTIVE,
                difficulty=Difficulty.MEDIUM,
                subject="Python Programming",
                topic="Data Structures",
                content="Explain the difference between a list and a tuple in Python. When would you use each?",
                points=15,
                max_words=200
            ),
            Question(
                id="q4",
                type=QuestionType.SUBJECTIVE,
                category=QuestionType.SUBJECTIVE,
                difficulty=Difficulty.MEDIUM,
                subject="Python Programming",
                topic="Advanced Concepts",
                content="What is a Python decorator? Provide a simple example of when you might use one.",
                points=15,
                max_words=200
            ),
            Question(
                id="q5",
                type=QuestionType.CODING,
                category=QuestionType.CODING,
                difficulty=Difficulty.MEDIUM,
                subject="Python Programming",
                topic="String Manipulation",
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
                category=QuestionType.CODING,
                difficulty=Difficulty.MEDIUM,
                subject="Data Structures & Algorithms",
                topic="Arrays",
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

# Initialize question loader
question_loader = QuestionLoader()

# Create a new demo exam with questions from the question bank
def create_categorized_exam():
    """Create exam with questions from the question bank."""
    import uuid
    
    # Load questions from bank
    mcq_questions = question_loader.get_random_questions('mcq', count=3, difficulty='easy')
    coding_questions = question_loader.get_random_questions('coding', count=2)
    subjective_questions = question_loader.get_random_questions('subjective', count=2, difficulty='medium')
    
    questions = []
    
    # Add MCQ questions
    for q in mcq_questions:
        questions.append(Question(
            id=str(uuid.uuid4()),
            type=QuestionType.MCQ,
            category=QuestionType.MCQ,
            difficulty=getattr(Difficulty, q.get('difficulty', 'medium').upper()),
            subject=q.get('subject'),
            topic=q.get('topic'),
            content=q['content'],
            points=q.get('points', 5),
            options=[MCQOption(**opt) for opt in q.get('options', [])],
            correct_option=q.get('correct_option'),
            tags=q.get('tags'),
            source=q.get('source')
        ))
    
    # Add Coding questions
    for q in coding_questions:
        questions.append(Question(
            id=str(uuid.uuid4()),
            type=QuestionType.CODING,
            category=QuestionType.CODING,
            difficulty=getattr(Difficulty, q.get('difficulty', 'medium').upper()),
            subject=q.get('subject'),
            topic=q.get('topic'),
            content=q['content'],
            points=q.get('points', 20),
            code_template=q.get('code_template'),
            language=q.get('language', 'python'),
            test_cases=q.get('test_cases', []),
            tags=q.get('tags'),
            source=q.get('source')
        ))
    
    # Add Subjective questions
    for q in subjective_questions:
        questions.append(Question(
            id=str(uuid.uuid4()),
            type=QuestionType.SUBJECTIVE,
            category=QuestionType.SUBJECTIVE,
            difficulty=getattr(Difficulty, q.get('difficulty', 'medium').upper()),
            subject=q.get('subject'),
            topic=q.get('topic'),
            content=q['content'],
            points=q.get('points', 15),
            min_words=q.get('min_words'),
            max_words=q.get('max_words'),
            rubric=q.get('rubric'),
            tags=q.get('tags'),
            source=q.get('source')
        ))
    
    return Exam(
        id="categorized-exam-1",
        title="Comprehensive Programming Assessment",
        description="Multi-category exam with MCQ, Coding, and Subjective questions covering Python, Algorithms, and CS fundamentals.",
        duration_minutes=60,
        questions=questions
    )

# Add the categorized exam to mock exams
try:
    MOCK_EXAMS["categorized-exam-1"] = create_categorized_exam()
except Exception as e:
    print(f"Warning: Could not create categorized exam: {e}")

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


class UpdateExamRequest(BaseModel):
    """Request to update an exam."""
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None


@router.patch("/{exam_id}")
async def update_exam(exam_id: str, request: UpdateExamRequest):
    """Update an existing exam (user-created only)."""
    if exam_id not in exams_db:
        raise HTTPException(status_code=404, detail="Exam not found in custom exams")

    exam = exams_db[exam_id]
    if request.title is not None:
        exam.title = request.title
    if request.description is not None:
        exam.description = request.description
    if request.duration_minutes is not None:
        exam.duration_minutes = request.duration_minutes

    return {"message": "Exam updated", "exam_id": exam_id}


@router.delete("/{exam_id}")
async def delete_exam(exam_id: str):
    """Delete an exam (user-created only, not mock exams)."""
    if exam_id not in exams_db:
        raise HTTPException(status_code=404, detail="Exam not found in custom exams")

    del exams_db[exam_id]
    return {"message": "Exam deleted", "exam_id": exam_id}


class ScheduleExamRequest(BaseModel):
    """Request to schedule an exam."""
    scheduled_start: Optional[str] = None  # ISO datetime
    scheduled_end: Optional[str] = None


@router.patch("/{exam_id}/publish")
async def publish_exam(exam_id: str):
    """Toggle publish state for an exam."""
    if exam_id not in exams_db:
        raise HTTPException(status_code=404, detail="Exam not found in custom exams")

    exam = exams_db[exam_id]
    # Toggle with a simple attribute check
    current = getattr(exam, '_published', False)
    exam._published = not current  # type: ignore[attr-defined]
    return {"message": f"Exam {'published' if exam._published else 'unpublished'}", "is_published": exam._published}


@router.patch("/{exam_id}/schedule")
async def schedule_exam(exam_id: str, request: ScheduleExamRequest):
    """Set scheduling window for an exam."""
    from datetime import datetime as dt

    if exam_id not in exams_db:
        raise HTTPException(status_code=404, detail="Exam not found in custom exams")

    start = None
    end = None
    if request.scheduled_start:
        try:
            start = dt.fromisoformat(request.scheduled_start)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid scheduled_start format")
    if request.scheduled_end:
        try:
            end = dt.fromisoformat(request.scheduled_end)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid scheduled_end format")

    if start and end and end <= start:
        raise HTTPException(status_code=422, detail="scheduled_end must be after scheduled_start")

    exam = exams_db[exam_id]
    exam._scheduled_start = start  # type: ignore[attr-defined]
    exam._scheduled_end = end  # type: ignore[attr-defined]

    return {
        "message": "Exam scheduled",
        "scheduled_start": request.scheduled_start,
        "scheduled_end": request.scheduled_end,
    }


@router.get("/categories")
async def get_categories():
    """Get list of available question categories."""
    return {
        "categories": [
            {"id": "mcq", "name": "Multiple Choice Questions", "description": "Questions with predefined options"},
            {"id": "coding", "name": "Coding Problems", "description": "Programming challenges with test cases"},
            {"id": "subjective", "name": "Subjective Questions", "description": "Essay and short answer questions"}
        ]
    }


@router.get("/subjects")
async def get_subjects(category: Optional[str] = None):
    """Get list of available subjects."""
    loader = QuestionLoader()
    subjects = loader.get_subjects(category)
    return {"subjects": subjects}


@router.get("/topics")
async def get_topics(subject: Optional[str] = None):
    """Get list of available topics."""
    loader = QuestionLoader()
    topics = loader.get_topics(subject)
    return {"topics": topics}


@router.get("/questions/search")
async def search_questions(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags")
):
    """Search and filter questions from the question bank."""
    loader = QuestionLoader()
    
    if category:
        questions = loader.load_category(category)
    else:
        all_qs = loader.load_all()
        questions = []
        for qs in all_qs.values():
            questions.extend(qs)
    
    # Apply filters
    tag_list = tags.split(',') if tags else None
    filtered = loader.filter_questions(
        questions,
        difficulty=difficulty,
        subject=subject,
        topic=topic,
        tags=tag_list
    )
    
    # Convert to Question models (without answers)
    result = []
    for idx, q in enumerate(filtered):
        q_copy = q.copy()
        if 'correct_option' in q_copy:
            del q_copy['correct_option']
        if 'explanation' in q_copy:
            del q_copy['explanation']
        if 'id' not in q_copy:
            q_copy['id'] = f"q_{idx}"
        result.append(q_copy)
    
    return {"questions": result, "count": len(result)}


@router.get("/questions/random")
async def get_random_questions(
    category: str = Query(..., description="Category to select from"),
    count: int = Query(5, description="Number of questions to get"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    subject: Optional[str] = Query(None, description="Filter by subject")
):
    """Get random questions from the question bank."""
    loader = QuestionLoader()
    
    questions = loader.get_random_questions(
        category=category,
        count=count,
        difficulty=difficulty,
        subject=subject
    )
    
    # Convert to Question models (without answers)
    result = []
    for idx, q in enumerate(questions):
        q_copy = q.copy()
        if 'correct_option' in q_copy:
            del q_copy['correct_option']
        if 'explanation' in q_copy:
            del q_copy['explanation']
        if 'id' not in q_copy:
            q_copy['id'] = str(uuid.uuid4())
        result.append(q_copy)
    
    return {"questions": result, "count": len(result)}


@router.get("/{exam_id}/by-category")
async def get_exam_by_category(exam_id: str, include_answers: bool = False):
    """Get exam questions grouped by category."""
    all_exams = {**MOCK_EXAMS, **exams_db}
    
    if exam_id not in all_exams:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exam = all_exams[exam_id]
    
    # Group questions by category
    categorized = {
        "mcq": [],
        "coding": [],
        "subjective": []
    }
    
    for q in exam.questions:
        q_dict = q.model_dump() if hasattr(q, 'model_dump') else q.dict()
        
        # Remove answers if not requested
        if not include_answers:
            if 'correct_option' in q_dict:
                del q_dict['correct_option']
            if 'explanation' in q_dict:
                del q_dict['explanation']
        
        # Determine category
        category = q_dict.get('category') or q_dict.get('type')
        
        if category in categorized:
            categorized[category].append(q_dict)
    
    return {
        "id": exam.id,
        "title": exam.title,
        "description": exam.description,
        "duration_minutes": exam.duration_minutes,
        "categories": categorized,
        "total_questions": len(exam.questions)
    }

