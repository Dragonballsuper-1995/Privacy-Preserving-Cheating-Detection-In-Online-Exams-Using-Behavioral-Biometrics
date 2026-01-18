"""
Script to create a demo exam with all three categories
"""

import sys
import uuid
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.question_loader import QuestionLoader
from app.api.exams import Question, Exam, QuestionType, Difficulty, MCQOption


def create_categorized_demo_exam():
    """Create a demo exam with questions from all three categories."""
    
    # Initialize loader
    loader = QuestionLoader()
    
    # Load questions
    mcq_questions = loader.get_random_questions('mcq', count=3, difficulty='easy')
    coding_questions = loader.get_random_questions('coding', count=2, difficulty='easy')
    subjective_questions = loader.get_random_questions('subjective', count=2, difficulty='medium')
    
    # Convert to Question objects
    questions = []
    
    # Add MCQ questions
    for q in mcq_questions:
        questions.append(Question(
            id=str(uuid.uuid4()),
            type=QuestionType.MCQ,
            category=QuestionType.MCQ,
            difficulty=getattr(Difficulty, q.get('difficulty', 'medium').upper()),
            content=q['content'],
            points=q.get('points', 5),
            subject=q.get('subject'),
            topic=q.get('topic'),
            tags=q.get('tags'),
            source=q.get('source'),
            explanation=q.get('explanation'),
            options=[MCQOption(**opt) for opt in q.get('options', [])],
            correct_option=q.get('correct_option')
        ))
    
    # Add Coding questions
    for q in coding_questions:
        questions.append(Question(
            id=str(uuid.uuid4()),
            type=QuestionType.CODING,
            category=QuestionType.CODING,
            difficulty=getattr(Difficulty, q.get('difficulty', 'medium').upper()),
            content=q['content'],
            points=q.get('points', 20),
            subject=q.get('subject'),
            topic=q.get('topic'),
            tags=q.get('tags'),
            source=q.get('source'),
            code_template=q.get('code_template'),
            language=q.get('language', 'python'),
            test_cases=q.get('test_cases', [])
        ))
    
    # Add Subjective questions
    for q in subjective_questions:
        questions.append(Question(
            id=str(uuid.uuid4()),
            type=QuestionType.SUBJECTIVE,
            category=QuestionType.SUBJECTIVE,
            difficulty=getattr(Difficulty, q.get('difficulty', 'medium').upper()),
            content=q['content'],
            points=q.get('points', 15),
            subject=q.get('subject'),
            topic=q.get('topic'),
            tags=q.get('tags'),
            source=q.get('source'),
            explanation=q.get('explanation'),
            min_words=q.get('min_words'),
            max_words=q.get('max_words'),
            rubric=q.get('rubric')
        ))
    
    # Create exam
    exam = Exam(
        id="categorized-demo-1",
        title="Comprehensive Programming Assessment",
        description="Multi-category exam covering MCQ, Coding, and Subjective questions across Python, Algorithms, and Computer Science fundamentals.",
        duration_minutes=60,
        questions=questions
    )
    
    return exam


if __name__ == "__main__":
    exam = create_categorized_demo_exam()
    print(f"Created exam: {exam.title}")
    print(f"Total questions: {len(exam.questions)}")
    
    # Count by category
    mcq = sum(1 for q in exam.questions if q.category == QuestionType.MCQ)
    coding = sum(1 for q in exam.questions if q.category == QuestionType.CODING)
    subjective = sum(1 for q in exam.questions if q.category == QuestionType.SUBJECTIVE)
    
    print(f"  MCQ: {mcq}")
    print(f"  Coding: {coding}")
    print(f"  Subjective: {subjective}")
