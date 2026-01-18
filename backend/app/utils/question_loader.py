"""
Question Loader Utility
Loads questions from JSON files and validates them
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path


class QuestionLoader:
    """Utility to load questions from JSON files."""
    
    def __init__(self, questions_dir: str = None):
        """
        Initialize the question loader.
        
        Args:
            questions_dir: Path to the questions directory. 
                          Defaults to backend/data/questions
        """
        if questions_dir is None:
            # Get the backend/data/questions directory
            current_dir = Path(__file__).parent.parent.parent
            self.questions_dir = current_dir / "data" / "questions"
        else:
            self.questions_dir = Path(questions_dir)
    
    def load_from_file(self, file_path: str) -> Dict:
        """
        Load questions from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary with meta and questions
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate structure
        if 'questions' not in data:
            raise ValueError(f"Invalid question file: {file_path}. Missing 'questions' key.")
        
        return data
    
    def load_category(self, category: str) -> List[Dict]:
        """
        Load all questions for a specific category.
        
        Args:
            category: One of 'mcq', 'coding', 'subjective'
            
        Returns:
            List of question dictionaries
        """
        category_dir = self.questions_dir / category
        
        if not category_dir.exists():
            return []
        
        all_questions = []
        
        for json_file in category_dir.glob("*.json"):
            try:
                data = self.load_from_file(json_file)
                questions = data.get('questions', [])
                
                # Ensure category is set
                for q in questions:
                    q['category'] = category
                
                all_questions.extend(questions)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        return all_questions
    
    def load_all(self) -> Dict[str, List[Dict]]:
        """
        Load all questions from all categories.
        
        Returns:
            Dictionary mapping category to list of questions
        """
        return {
            'mcq': self.load_category('mcq'),
            'coding': self.load_category('coding'),
            'subjective': self.load_category('subjective')
        }
    
    def filter_questions(
        self,
        questions: List[Dict],
        difficulty: Optional[str] = None,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Filter questions based on criteria.
        
        Args:
            questions: List of question dictionaries
            difficulty: Filter by difficulty level
            subject: Filter by subject
            topic: Filter by topic
            tags: Filter by tags (any match)
            
        Returns:
            Filtered list of questions
        """
        filtered = questions
        
        if difficulty:
            filtered = [q for q in filtered if q.get('difficulty') == difficulty]
        
        if subject:
            filtered = [q for q in filtered if q.get('subject') == subject]
        
        if topic:
            filtered = [q for q in filtered if q.get('topic') == topic]
        
        if tags:
            filtered = [
                q for q in filtered 
                if q.get('tags') and any(tag in q['tags'] for tag in tags)
            ]
        
        return filtered
    
    def get_random_questions(
        self,
        category: str,
        count: int,
        difficulty: Optional[str] = None,
        subject: Optional[str] = None
    ) -> List[Dict]:
        """
        Get random questions from a category.
        
        Args:
            category: Category to select from
            count: Number of questions to select
            difficulty: Optional difficulty filter
            subject: Optional subject filter
            
        Returns:
            List of random questions
        """
        import random
        
        questions = self.load_category(category)
        
        # Apply filters
        if difficulty or subject:
            questions = self.filter_questions(
                questions,
                difficulty=difficulty,
                subject=subject
            )
        
        # Select random questions
        if len(questions) <= count:
            return questions
        
        return random.sample(questions, count)
    
    def validate_question(self, question: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate a question dictionary.
        
        Args:
            question: Question dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['content', 'type', 'category', 'difficulty', 'points']
        
        for field in required_fields:
            if field not in question:
                return False, f"Missing required field: {field}"
        
        # Validate category-specific fields
        q_type = question['type']
        
        if q_type == 'mcq':
            if 'options' not in question or 'correct_option' not in question:
                return False, "MCQ must have 'options' and 'correct_option'"
            
            if len(question['options']) < 2:
                return False, "MCQ must have at least 2 options"
        
        elif q_type == 'coding':
            if 'code_template' not in question or 'test_cases' not in question:
                return False, "Coding question must have 'code_template' and 'test_cases'"
            
            if not question['test_cases']:
                return False, "Coding question must have at least 1 test case"
        
        elif q_type == 'subjective':
            # Subjective questions are more flexible
            pass
        
        return True, None
    
    def get_subjects(self, category: Optional[str] = None) -> List[str]:
        """
        Get list of unique subjects.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of subject names
        """
        if category:
            questions = self.load_category(category)
        else:
            all_questions = self.load_all()
            questions = []
            for qs in all_questions.values():
                questions.extend(qs)
        
        subjects = set(q.get('subject') for q in questions if q.get('subject'))
        return sorted(list(subjects))
    
    def get_topics(self, subject: Optional[str] = None) -> List[str]:
        """
        Get list of unique topics.
        
        Args:
            subject: Optional subject filter
            
        Returns:
            List of topic names
        """
        all_questions = self.load_all()
        questions = []
        for qs in all_questions.values():
            questions.extend(qs)
        
        if subject:
            questions = [q for q in questions if q.get('subject') == subject]
        
        topics = set(q.get('topic') for q in questions if q.get('topic'))
        return sorted(list(topics))
