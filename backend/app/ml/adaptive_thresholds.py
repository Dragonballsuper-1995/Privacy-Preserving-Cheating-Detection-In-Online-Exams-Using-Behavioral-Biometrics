"""
Adaptive Threshold System

Dynamically adjusts risk thresholds based on exam type, student history, and performance data.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
import statistics


@dataclass
class ThresholdConfig:
    """Configuration for adaptive thresholds."""
    base_threshold: float = 0.75
    exam_type_multiplier: Dict[str, float] = None
    confidence_adjustment: float = 0.1
    history_weight: float = 0.3
    
    def __post_init__(self):
        if self.exam_type_multiplier is None:
            self.exam_type_multiplier = {
                "quiz": 0.9,          # More lenient for quizzes
                "midterm": 1.0,       # Standard threshold
                "final": 1.1,         # Stricter for finals
                "certification": 1.2  # Strictest for certifications
            }


class AdaptiveThresholdSystem:
    """
    Manages adaptive thresholds for cheating detection.
    
    Adjusts thresholds based on:
    - Exam type and importance
    - Student's historical performance
    - Model confidence
    - Population statistics
    """
    
    def __init__(self, config: ThresholdConfig = None):
        self.config = config or ThresholdConfig()
        self.population_stats = {}  # exam_id -> statistics
        self.student_history = {}   # student_id -> history
    
    def get_threshold(
        self,
        exam_type: str = "midterm",
        student_id: Optional[str] = None,
        model_confidence: float = 0.8,
        exam_id: Optional[str] = None
    ) -> float:
        """
        Calculate adaptive threshold for a specific context.
        
        Args:
            exam_type: Type of exam (quiz, midterm, final, certification)
            student_id: Student identifier
            model_confidence: Model's confidence in prediction (0-1)
            exam_id: Exam identifier
            
        Returns:
            Adjusted threshold value
        """
        # Start with base threshold
        threshold = self.config.base_threshold
        
        # Adjust for exam type
        exam_multiplier = self.config.exam_type_multiplier.get(exam_type, 1.0)
        threshold *= exam_multiplier
        
        # Adjust for model confidence
        # Higher confidence -> can use lower threshold
        # Lower confidence -> need higher threshold to avoid false positives
        confidence_adjustment = (1 - model_confidence) * self.config.confidence_adjustment
        threshold += confidence_adjustment
        
        # Adjust based on student history
        if student_id and student_id in self.student_history:
            history_adjustment = self._calculate_history_adjustment(student_id)
            threshold += history_adjustment
        
        # Adjust based on exam population statistics
        if exam_id and exam_id in self.population_stats:
            population_adjustment = self._calculate_population_adjustment(exam_id)
            threshold += population_adjustment
        
        # Ensure threshold stays in valid range
        threshold = max(0.5, min(0.95, threshold))
        
        return threshold
    
    def _calculate_history_adjustment(self, student_id: str) -> float:
        """
        Calculate threshold adjustment based on student's history.
        
        Students with clean history -> slightly lower threshold
        Students with past flags -> slightly higher threshold
        """
        history = self.student_history.get(student_id, {})
        
        total_exams = history.get("total_exams", 0)
        flagged_exams = history.get("flagged_exams", 0)
        
        if total_exams == 0:
            return 0.0  # No history, no adjustment
        
        flag_rate = flagged_exams / total_exams
        
        if flag_rate == 0:
            # Clean history: slightly more lenient
            return -0.05 * self.config.history_weight
        elif flag_rate > 0.3:
            # Frequent flags: slightly stricter
            return 0.1 * self.config.history_weight
        else:
            # Some flags but not excessive
            return 0.05 * self.config.history_weight
    
    def _calculate_population_adjustment(self, exam_id: str) -> float:
        """
        Calculate threshold adjustment based on exam population.
        
        If exam has unusually high flagging rate, might adjust threshold up
        to avoid over-flagging due to exam difficulty or design.
        """
        stats = self.population_stats.get(exam_id, {})
        
        avg_risk_score = stats.get("avg_risk_score", 0.3)
        std_risk_score = stats.get("std_risk_score", 0.2)
        
        # If population average is high, might be a difficult exam
        # Adjust threshold upward slightly
        if avg_risk_score > 0.4:
            return 0.05
        elif avg_risk_score < 0.2:
            # Very low average might mean easy exam or good students
            return -0.03
        
        return 0.0
    
    def update_student_history(
        self,
        student_id: str,
        was_flagged: bool,
        risk_score: float
    ):
        """
        Update student's historical data.
        
        Args:
            student_id: Student identifier
            was_flagged: Whether this exam was flagged
            risk_score: Risk score for this exam
        """
        if student_id not in self.student_history:
            self.student_history[student_id] = {
                "total_exams": 0,
                "flagged_exams": 0,
                "risk_scores": []
            }
        
        history = self.student_history[student_id]
        history["total_exams"] += 1
        if was_flagged:
            history["flagged_exams"] += 1
        history["risk_scores"].append(risk_score)
        
        # Keep only last 10 exams
        if len(history["risk_scores"]) > 10:
            history["risk_scores"] = history["risk_scores"][-10:]
    
    def update_population_stats(
        self,
        exam_id: str,
        risk_scores: List[float]
    ):
        """
        Update population statistics for an exam.
        
        Args:
            exam_id: Exam identifier
            risk_scores: List of all risk scores for this exam
        """
        if not risk_scores:
            return
        
        self.population_stats[exam_id] = {
            "avg_risk_score": statistics.mean(risk_scores),
            "median_risk_score": statistics.median(risk_scores),
            "std_risk_score": statistics.stdev(risk_scores) if len(risk_scores) > 1 else 0.0,
            "sample_size": len(risk_scores)
        }
    
    def calibrate_for_exam(
        self,
        exam_id: str,
        historical_scores: List[float],
        target_flag_rate: float = 0.1
    ) -> float:
        """
        Calibrate threshold to achieve target flagging rate.
        
        Args:
            exam_id: Exam identifier
            historical_scores: Historical risk scores for similar exams
            target_flag_rate: Desired flagging rate (e.g., 0.1 = 10%)
            
        Returns:
            Calibrated threshold
        """
        if not historical_scores:
            return self.config.base_threshold
        
        # Sort scores
        sorted_scores = sorted(historical_scores, reverse=True)
        
        # Find threshold that would flag approximately target_flag_rate
        target_index = int(len(sorted_scores) * target_flag_rate)
        
        if target_index >= len(sorted_scores):
            return self.config.base_threshold
        
        calibrated_threshold = sorted_scores[target_index]
        
        # Ensure reasonable threshold
        calibrated_threshold = max(0.5, min(0.95, calibrated_threshold))
        
        return calibrated_threshold
    
    def get_recommendations(
        self,
        exam_type: str,
        expected_difficulty: str = "medium",
        student_count: int = 100
    ) -> Dict[str, any]:
        """
        Get threshold recommendations for an upcoming exam.
        
        Args:
            exam_type: Type of exam
            expected_difficulty: Expected difficulty (easy/medium/hard)
            student_count: Number of expected students
            
        Returns:
            Dictionary with threshold recommendations
        """
        base = self.config.base_threshold
        exam_mult = self.config.exam_type_multiplier.get(exam_type, 1.0)
        
        recommended_threshold = base * exam_mult
        
        # Adjust for difficulty
        difficulty_adjustment = {
            "easy": -0.05,
            "medium": 0.0,
            "hard": 0.05
        }.get(expected_difficulty, 0.0)
        
        recommended_threshold += difficulty_adjustment
        
        # Estimate expected flags
        expected_flag_rate = 0.10  # Assume 10% baseline
        expected_flags = int(student_count * expected_flag_rate)
        
        return {
            "recommended_threshold": round(recommended_threshold, 3),
            "base_threshold": base,
            "exam_type_multiplier": exam_mult,
            "difficulty_adjustment": difficulty_adjustment,
            "expected_flags": expected_flags,
            "expected_flag_rate": expected_flag_rate,
            "confidence": "medium",
            "notes": f"Threshold calibrated for {exam_type} exam with {expected_difficulty} difficulty"
        }
