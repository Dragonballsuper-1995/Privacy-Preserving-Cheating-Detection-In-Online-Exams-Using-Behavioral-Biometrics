"""
Question Navigation Pattern Analysis

Analyzes how students navigate through exam questions:
- Question order (sequential vs. random)
- Time distribution across questions
- Return patterns (revisiting questions)
- Skip behavior (skipped questions answered later)
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import statistics


@dataclass
class NavigationFeatures:
    """Features related to question navigation patterns."""
    # Question access patterns
    total_questions: int = 0
    questions_accessed: int = 0
    access_order_entropy: float = 0.0  # Random vs. sequential
    
    # Time distribution
    avg_time_per_question: float = 0.0
    time_variance: float = 0.0
    questions_under_30s: int = 0  # Suspiciously fast
    questions_over_10min: int = 0  # Unusually slow
    
    # Navigation patterns
    forward_nav_count: int = 0  # Next question
    backward_nav_count: int = 0  # Previous question
    jump_nav_count: int = 0  # Jump to specific question
    
    # Return patterns
    questions_revisited: int = 0
    avg_revisit_count: float = 0.0
    max_revisit_count: int = 0
    
    # Skip behavior
    questions_skipped: int = 0
    skipped_then_answered: int = 0
    skip_pattern_score: float = 0.0  # Suspicious if high
    
    # Answer completion patterns
    questions_changed_after_completion: int = 0
    late_completions: int = 0  # Answered near end of exam
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_questions": self.total_questions,
            "questions_accessed": self.questions_accessed,
            "access_order_entropy": self.access_order_entropy,
            "avg_time_per_question": self.avg_time_per_question,
            "time_variance": self.time_variance,
            "questions_under_30s": self.questions_under_30s,
            "questions_over_10min": self.questions_over_10min,
            "forward_nav_count": self.forward_nav_count,
            "backward_nav_count": self.backward_nav_count,
            "jump_nav_count": self.jump_nav_count,
            "questions_revisited": self.questions_revisited,
            "avg_revisit_count": self.avg_revisit_count,
            "max_revisit_count": self.max_revisit_count,
            "questions_skipped": self.questions_skipped,
            "skipped_then_answered": self.skipped_then_answered,
            "skip_pattern_score": self.skip_pattern_score,
            "questions_changed_after_completion": self.questions_changed_after_completion,
            "late_completions": self.late_completions,
        }


def calculate_sequence_entropy(sequence: List[int]) -> float:
    """
    Calculate entropy of question access sequence.
    
    Higher entropy = more random access.
    Lower entropy = more sequential access.
    """
    if len(sequence) < 2:
        return 0.0
    
    # Count transitions between questions
    transitions = {}
    
    for i in range(len(sequence) - 1):
        current = sequence[i]
        next_q = sequence[i + 1]
        transition = (current, next_q)
        transitions[transition] = transitions.get(transition, 0) + 1
    
    # Calculate entropy
    total_transitions = len(sequence) - 1
    entropy = 0.0
    
    for count in transitions.values():
        if count > 0:
            probability = count / total_transitions
            import math
            entropy -= probability * math.log2(probability)
    
    return entropy


def extract_navigation_features(
    events: List[Dict[str, Any]],
    total_questions: int = 10
) -> NavigationFeatures:
    """
    Extract question navigation features from events.
    
    Args:
        events: List of event dictionaries
        total_questions: Total number of questions in exam
        
    Returns:
        NavigationFeatures dataclass with extracted features
    """
    features = NavigationFeatures()
    features.total_questions = total_questions
    
    # Track question access
    question_visits = {}  # question_id -> list of timestamps
    access_sequence = []  # Ordered list of question IDs
    current_question = None
    question_entry_time = None
    
    question_times = {}  # question_id -> total time spent
    
    for event in events:
        event_type = event.get("event_type")
        data = event.get("data", {})
        timestamp = event.get("timestamp", 0)
        
        # Track question navigation
        if event_type == "navigation":
            new_question = data.get("question_id")
            nav_type = data.get("type", "jump")
            
            # Calculate time spent on previous question
            if current_question is not None and question_entry_time is not None:
                time_spent = timestamp - question_entry_time
                question_times[current_question] = question_times.get(current_question, 0) + time_spent
            
            # Record navigation type
            if nav_type == "next":
                features.forward_nav_count += 1
            elif nav_type == "previous":
                features.backward_nav_count += 1
            else:
                features.jump_nav_count += 1
            
            # Track question visits
            if new_question not in question_visits:
                question_visits[new_question] = []
            question_visits[new_question].append(timestamp)
            access_sequence.append(new_question)
            
            # Update current question
            current_question = new_question
            question_entry_time = timestamp
    
    # Analyze question access patterns
    features.questions_accessed = len(question_visits)
    
    # Calculate access order entropy
    if access_sequence:
        # Convert question IDs to numeric sequence for entropy calculation
        unique_questions = list(set(access_sequence))
        question_to_idx = {q: i for i, q in enumerate(unique_questions)}
        numeric_sequence = [question_to_idx[q] for q in access_sequence]
        features.access_order_entropy = calculate_sequence_entropy(numeric_sequence)
    
    # Analyze time distribution
    if question_times:
        times = list(question_times.values())
        features.avg_time_per_question = statistics.mean(times)
        features.time_variance = statistics.variance(times) if len(times) > 1 else 0.0
        
        # Count questions with unusual times
        for time in times:
            if time < 30000:  # < 30 seconds
                features.questions_under_30s += 1
            if time > 600000:  # > 10 minutes
                features.questions_over_10min += 1
    
    # Analyze revisit patterns
    revisit_counts = []
    for question_id, visits in question_visits.items():
        visit_count = len(visits)
        if visit_count > 1:
            features.questions_revisited += 1
            revisit_counts.append(visit_count - 1)  # Number of REvisits
    
    if revisit_counts:
        features.avg_revisit_count = statistics.mean(revisit_counts)
        features.max_revisit_count = max(revisit_counts)
    
    # Detect skip patterns
    # A question is skipped if accessed but then left quickly (<10s) and revisited later
    skipped_questions = set()
    skipped_then_answered = set()
    
    for question_id, visits in question_visits.items():
        if len(visits) >= 2:
            # Check if first visit was very short
            if len(question_times.get(question_id, [0])) > 0:
                first_visit_time = question_times.get(question_id, 0)
                if first_visit_time < 10000:  # < 10 seconds on first visit
                    skipped_questions.add(question_id)
                    # Check if it was answered later (longer time on second visit)
                    if len(visits) >= 2:
                        skipped_then_answered.add(question_id)
    
    features.questions_skipped = len(skipped_questions)
    features.skipped_then_answered = len(skipped_then_answered)
    
    # Calculate skip pattern score
    # High score if many questions skipped and then answered perfectly later
    if features.questions_accessed > 0:
        features.skip_pattern_score = features.skipped_then_answered / features.questions_accessed
    
    return features


def calculate_navigation_anomaly_score(features: NavigationFeatures) -> float:
    """
    Calculate anomaly score based on navigation patterns.
    
    Higher scores indicate more suspicious navigation behavior.
    
    Args:
        features: NavigationFeatures dataclass
        
    Returns:
        Anomaly score between 0 and 1
    """
    score = 0.0
    
    # Many questions answered very quickly (< 30s) is suspicious
    if features.questions_under_30s > features.total_questions * 0.3:
        score += 0.25
    
    # High skip pattern score suggests looking up answers elsewhere
    if features.skip_pattern_score > 0.4:
        score += 0.30
    
    # Very high jump navigation (vs. sequential) might indicate pre-knowledge
    total_nav = features.forward_nav_count + features.backward_nav_count + features.jump_nav_count
    if total_nav > 0:
        jump_ratio = features.jump_nav_count / total_nav
        if jump_ratio > 0.7:
            score += 0.15
    
    # Low access order entropy with high jumps = suspicious
    if features.access_order_entropy < 1.0 and features.jump_nav_count > 5:
        score += 0.20
    
    # Many questions changed after completion might indicate receiving answers
    if features.questions_changed_after_completion > features.total_questions * 0.3:
        score += 0.15
    
    return min(score, 1.0)
