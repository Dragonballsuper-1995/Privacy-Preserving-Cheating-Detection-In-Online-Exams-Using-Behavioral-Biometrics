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
from app.ml.predictor import (
    MLPredictor,
    MLPrediction,
    predict_cheating,
    get_predictor,
)
from app.ml.derived_features import (
    DerivedFeatures,
    extract_derived_features,
    detect_bursts,
    compute_burst_bonus,
)

__all__ = [
    "AnswerSimilarityModel",
    "compute_similarity",
    "find_similar_answers",
    "BehaviorAnomalyDetector",
    "detect_anomalies",
    "RiskFusionModel",
    "compute_fused_risk",
    # New ML predictor
    "MLPredictor",
    "MLPrediction",
    "predict_cheating",
    "get_predictor",
    # Derived features
    "DerivedFeatures",
    "extract_derived_features",
    "detect_bursts",
    "compute_burst_bonus",
]

