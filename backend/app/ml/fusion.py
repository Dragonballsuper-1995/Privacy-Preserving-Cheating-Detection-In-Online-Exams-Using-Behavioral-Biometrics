"""
Risk Fusion Model

Combines multiple risk signals (behavioral features, anomaly scores, similarity)
into a final risk score using a trainable classifier.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import pickle
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from app.core.config import settings


@dataclass
class FusionResult:
    """Result of the risk fusion model."""
    session_id: str
    final_risk_score: float  # 0 to 1
    is_flagged: bool
    confidence: float  # Model confidence
    
    # Component scores
    behavioral_score: float
    anomaly_score: float
    similarity_score: float
    
    # Explanation
    risk_factors: List[str] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "final_risk_score": self.final_risk_score,
            "is_flagged": self.is_flagged,
            "confidence": self.confidence,
            "behavioral_score": self.behavioral_score,
            "anomaly_score": self.anomaly_score,
            "similarity_score": self.similarity_score,
            "risk_factors": self.risk_factors,
            "risk_level": self.risk_level,
        }


class RiskFusionModel:
    """
    Combines multiple risk signals into a final cheating risk score.
    
    Uses a weighted ensemble approach with optional ML-based fusion.
    """
    
    # Default weights for different risk components
    DEFAULT_WEIGHTS = {
        "behavioral": 0.35,  # Feature-based behavioral score
        "anomaly": 0.35,     # Isolation Forest anomaly score
        "similarity": 0.30,  # Answer similarity score
    }
    
    # Risk level thresholds
    RISK_LEVELS = {
        "low": (0, 0.3),
        "medium": (0.3, 0.6),
        "high": (0.6, 0.8),
        "critical": (0.8, 1.0),
    }
    
    def __init__(
        self,
        use_ml: bool = True,
        flag_threshold: float = 0.75,
        model_path: Optional[str] = None
    ):
        """
        Initialize the fusion model.
        
        Args:
            use_ml: Whether to use ML model (if trained) or weighted average
            flag_threshold: Threshold for flagging sessions
            model_path: Path to load/save trained model
        """
        self.use_ml = use_ml
        self.flag_threshold = flag_threshold
        self.model_path = model_path or os.path.join(settings.models_dir, "fusion_model.pkl")
        
        # ML components
        self.scaler = StandardScaler()
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
        )
        self._is_fitted = False
        
        # Try to load existing model
        self.load()
    
    def compute_risk(
        self,
        behavioral_score: float,
        anomaly_score: float,
        similarity_score: float,
        session_id: str = "",
        risk_factors: Optional[List[str]] = None
    ) -> FusionResult:
        """
        Compute the final fused risk score.
        
        Args:
            behavioral_score: Score from behavioral feature analysis (0-1)
            anomaly_score: Score from anomaly detection (0-1)
            similarity_score: Score from answer similarity (0-1)
            session_id: Session identifier
            risk_factors: Optional list of contributing factors
            
        Returns:
            FusionResult with final risk assessment
        """
        features = np.array([[behavioral_score, anomaly_score, similarity_score]])
        
        if self._is_fitted and self.use_ml:
            # Use trained ML model
            features_scaled = self.scaler.transform(features)
            
            # Get probability of cheating (class 1)
            proba = self.classifier.predict_proba(features_scaled)[0]
            final_score = proba[1] if len(proba) > 1 else proba[0]
            confidence = max(proba)
        else:
            # Use weighted average
            final_score = (
                self.DEFAULT_WEIGHTS["behavioral"] * behavioral_score +
                self.DEFAULT_WEIGHTS["anomaly"] * anomaly_score +
                self.DEFAULT_WEIGHTS["similarity"] * similarity_score
            )
            confidence = 0.7  # Default confidence for rule-based
        
        # Determine risk level
        risk_level = self._get_risk_level(final_score)
        
        return FusionResult(
            session_id=session_id,
            final_risk_score=float(final_score),
            is_flagged=final_score >= self.flag_threshold,
            confidence=float(confidence),
            behavioral_score=behavioral_score,
            anomaly_score=anomaly_score,
            similarity_score=similarity_score,
            risk_factors=risk_factors or [],
            risk_level=risk_level,
        )
    
    def _get_risk_level(self, score: float) -> str:
        """Determine risk level from score."""
        for level, (low, high) in self.RISK_LEVELS.items():
            if low <= score < high:
                return level
        return "critical" if score >= 0.8 else "low"
    
    def fit(
        self,
        training_data: List[Tuple[Dict[str, float], int]]
    ):
        """
        Train the fusion model on labeled data.
        
        Args:
            training_data: List of (scores_dict, label) where:
                - scores_dict: {"behavioral": float, "anomaly": float, "similarity": float}
                - label: 0 (honest) or 1 (cheating)
        """
        if len(training_data) < 10:
            print("⚠️ Not enough training data for fusion model")
            return
        
        X = np.array([
            [d["behavioral"], d["anomaly"], d["similarity"]]
            for d, _ in training_data
        ])
        y = np.array([label for _, label in training_data])
        
        # Fit scaler and classifier
        X_scaled = self.scaler.fit_transform(X)
        self.classifier.fit(X_scaled, y)
        self._is_fitted = True
        
        print(f"✅ Fusion model trained on {len(training_data)} samples")
        self.save()
    
    def save(self):
        """Save the trained model to disk."""
        if self._is_fitted:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    "classifier": self.classifier,
                    "scaler": self.scaler,
                }, f)
    
    def load(self) -> bool:
        """Load a trained model from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.classifier = data["classifier"]
                    self.scaler = data["scaler"]
                    self._is_fitted = True
                return True
            except Exception:
                return False
        return False


def compute_fused_risk(
    behavioral_score: float,
    anomaly_score: float,
    similarity_score: float = 0.0,
    session_id: str = "",
    risk_factors: Optional[List[str]] = None
) -> FusionResult:
    """
    Convenience function to compute fused risk score.
    
    Args:
        behavioral_score: Score from behavioral features (0-1)
        anomaly_score: Score from anomaly detection (0-1)
        similarity_score: Score from answer similarity (0-1)
        session_id: Session identifier
        risk_factors: List of contributing factors
        
    Returns:
        FusionResult with final risk assessment
    """
    model = RiskFusionModel(flag_threshold=settings.risk_threshold)
    return model.compute_risk(
        behavioral_score=behavioral_score,
        anomaly_score=anomaly_score,
        similarity_score=similarity_score,
        session_id=session_id,
        risk_factors=risk_factors,
    )
