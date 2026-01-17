"""
ML Package - Machine Learning models for cheating detection.
"""

from app.ml.embeddings import (
    AnswerSimilarityModel,
    compute_similarity,
    find_similar_answers,
)
from app.ml.anomaly import (
    BehaviorAnomalyDetector,
    detect_anomalies,
)
from app.ml.fusion import (
    RiskFusionModel,
    compute_fused_risk,
)

__all__ = [
    "AnswerSimilarityModel",
    "compute_similarity",
    "find_similar_answers",
    "BehaviorAnomalyDetector",
    "detect_anomalies",
    "RiskFusionModel",
    "compute_fused_risk",
]
