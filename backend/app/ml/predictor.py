"""
ML Predictor Module

Main interface for ML-based cheating detection.
Combines Random Forest classification with Isolation Forest anomaly detection.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import pickle
import os
import logging

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV

from app.core.config import settings
from app.ml.derived_features import (
    extract_derived_features,
    compute_burst_bonus,
    DerivedFeatures,
)

logger = logging.getLogger(__name__)


@dataclass
class MLPrediction:
    """Result of ML-based prediction."""
    
    probability: float  # 0.0-1.0 suspicion score
    confidence: str  # "high", "medium", "low"
    is_flagged: bool
    top_features: List[str] = field(default_factory=list)
    anomaly_detected: bool = False
    anomaly_reasons: List[str] = field(default_factory=list)
    burst_patterns: List[str] = field(default_factory=list)
    raw_rf_score: float = 0.0  # Raw Random Forest probability
    raw_if_score: float = 0.0  # Raw Isolation Forest anomaly score
    burst_bonus: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "probability": self.probability,
            "confidence": self.confidence,
            "is_flagged": self.is_flagged,
            "top_features": self.top_features,
            "anomaly_detected": self.anomaly_detected,
            "anomaly_reasons": self.anomaly_reasons,
            "burst_patterns": self.burst_patterns,
            "components": {
                "random_forest": self.raw_rf_score,
                "isolation_forest": self.raw_if_score,
                "burst_bonus": self.burst_bonus,
            }
        }


class MLPredictor:
    """
    Main ML-based cheating detector.
    
    Uses a hybrid approach:
    1. Random Forest for multi-feature classification
    2. Isolation Forest for single-metric anomaly detection
    3. Temporal burst pattern detection for additional context
    """
    
    # Feature names not needed as we use DictVectorizer
    
    def __init__(
        self,
        flag_threshold: float = 0.5,
        model_path: Optional[str] = None
    ):
        """
        Initialize the ML predictor.
        
        Args:
            flag_threshold: Probability threshold for flagging (0.0-1.0)
            model_path: Directory to load/save models
        """
        self.flag_threshold = flag_threshold
        # Default to the main models directory where train_model.py saves
        # We try multiple common paths to be robust
        possible_paths = [
            os.path.join("backend", "app", "ml", "models"),
            os.path.join("app", "ml", "models"),
            os.path.join(os.getcwd(), "backend", "app", "ml", "models"),
        ]
        
        self.model_path = model_path
        if not self.model_path:
            for path in possible_paths:
                if os.path.exists(path):
                    self.model_path = path
                    break
            
            # Fallback if nothing found
            if not self.model_path:
                 self.model_path = possible_paths[0]
        
        # Initialize models
        self.rf_model: Optional[RandomForestClassifier] = None
        self.if_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.vectorizer: Optional[Any] = None
        self.imputer: Optional[Any] = None
        self.is_trained = False
        
        # Try to load existing models
        self._load_models()
    
    def _flatten_features(self, features_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested dictionary features to match training data format."""
        flat = {}
        for key, value in features_dict.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (int, float, bool)):
                        if isinstance(sub_value, bool):
                            sub_value = int(sub_value)
                        flat[f"{key}_{sub_key}"] = sub_value
            elif isinstance(value, (int, float, bool)):
                if isinstance(value, bool):
                     value = int(value)
                flat[key] = value
        return flat

    def features_to_vector(
        self,
        raw_features: Dict[str, Any],
        derived: Optional[DerivedFeatures] = None
    ) -> Any:
        """
        Convert features to vector using the trained DictVectorizer.
        
        Args:
            raw_features: Dictionary from SessionFeatures.to_dict()
            derived: Pre-computed derived features (optional)
            
        Returns:
            Sparse matrix or numpy array of feature values
        """
        # Flatten features first
        flat_features = self._flatten_features(raw_features)
        
        # Add derived features if available
        if derived:
            flat_features.update(derived.to_dict())
            
        # Use vectorizer if available
        if self.vectorizer:
            try:
                # Transform returns a sparse matrix
                return self.vectorizer.transform([flat_features])
            except Exception as e:
                logger.error(f"Vectorization failed: {e}")
                return None
        
        return None
    
    def predict(
        self,
        raw_features: Dict[str, Any],
        events: Optional[List[Dict[str, Any]]] = None,
        session_id: str = ""
    ) -> MLPrediction:
        """
        Make ML-based prediction on a session.
        """
        # Extract derived features
        derived = extract_derived_features(raw_features, events)
        
        # Get burst bonus if events provided
        burst_bonus = 0.0
        burst_patterns = []
        if events:
            from app.ml.derived_features import detect_bursts
            bursts = detect_bursts(events)
            burst_bonus = sum(b.get("boost", 0) for b in bursts)
            burst_bonus = min(0.3, burst_bonus)  # Cap at 0.3
            burst_patterns = [b.get("description", "") for b in bursts]
        
        # ML Predictions
        rf_score = 0.0
        if_score = 0.0
        anomaly_detected = False
        anomaly_reasons = []
        
        # Check if we have a valid pipeline
        vector = self.features_to_vector(raw_features, derived)
        
        if self.is_trained and vector is not None:
            try:
                # 1. Impute (if needed)
                if self.imputer:
                    vector = self.imputer.transform(vector)
                
                # 2. Scale
                if self.scaler:
                    scaled = self.scaler.transform(vector)
                else:
                    scaled = vector
                
                # 3. Random Forest probability
                if self.rf_model:
                    rf_proba = self.rf_model.predict_proba(scaled)
                    rf_score = rf_proba[0][1]  # Probability of class 1 (cheating)
                
                # 4. Isolation Forest (not currently trained in train_model.py, but if it exists)
                if self.if_model:
                    if_pred = self.if_model.score_samples(scaled)
                    # Convert to 0-1 range (lower IF score = more anomalous)
                    # Score samples is typically negative for anomalies.
                    # e.g. -0.5 (anomaly) -> 0.75
                    # e.g. 0.5 (normal) -> 0.25
                    norm_score = 0.5 - (if_pred[0] / 2) # Rough normalization
                    if_score = max(0, min(1, norm_score))
                    anomaly_detected = if_pred[0] < -0.6  # Conservative threshold
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}")
                rf_score = self._heuristic_score(raw_features, derived)
        else:
            # Use heuristic fallback
            rf_score = self._heuristic_score(raw_features, derived)
            if_score = self._check_extreme_values(raw_features)
            # anomaly_detected = if_score > 0.7 
            # Disable anomaly detection in fallback to avoid false positives on new data
            anomaly_detected = False 
        
        # Check for extreme single metrics (always flag these)
        if not anomaly_detected:
            anomaly_detected, anomaly_reasons = self._detect_single_metric_anomalies(raw_features)
        
        # Combine scores
        # Weight: RF 60%, IF 20%, Burst 20%
        # If no IF model, redistrubute to RF
        if self.if_model:
            combined_score = (
                rf_score * 0.60 +
                if_score * 0.20 +
                burst_bonus * 0.20
            )
        else:
             combined_score = (
                rf_score * 0.80 +
                burst_bonus * 0.20
            )
        
        # Boost if anomaly detected
        if anomaly_detected:
            combined_score = max(combined_score, 0.6)
        
        # Clamp to 0-1
        final_probability = max(0, min(1, combined_score))
        
        # Determine confidence
        if final_probability >= 0.8 or final_probability <= 0.2:
            confidence = "high"
        elif final_probability >= 0.6 or final_probability <= 0.4:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Get top contributing features (approximate since we use sparse vector)
        top_features = self._get_top_features(raw_features, derived)
        
        return MLPrediction(
            probability=float(round(final_probability, 3)),
            confidence=confidence,
            is_flagged=bool(final_probability >= self.flag_threshold),
            top_features=top_features,
            anomaly_detected=bool(anomaly_detected),
            anomaly_reasons=anomaly_reasons,
            burst_patterns=burst_patterns,
            raw_rf_score=float(round(rf_score, 3)),
            raw_if_score=float(round(if_score, 3)),
            burst_bonus=float(round(burst_bonus, 3)),
        )
    
    def _heuristic_score(
        self,
        raw_features: Dict[str, Any],
        derived: DerivedFeatures
    ) -> float:
        """
        Calculate heuristic score when models aren't trained.
        
        Uses weighted sum with amplification.
        """
        # Use amplified scores for stronger signals
        score = (
            derived.paste_score_amplified * 0.30 +
            derived.focus_score_amplified * 0.20 +
            derived.hesitation_score_amplified * 0.15 +
            raw_features.get("typing_score", 0) * 0.10 +
            raw_features.get("text_score", 0) * 0.05 +
            derived.paste_after_blur_ratio * 0.10 +
            derived.burst_density * 0.05 / 10 +  # Normalize burst density
            derived.paste_to_typing_ratio * 0.05
        )
        
        return max(0, min(1, score))
    
    def _check_extreme_values(self, raw_features: Dict[str, Any]) -> float:
        """Check for extreme single metric values."""
        scores = [
            raw_features.get("paste_score", 0),
            raw_features.get("focus_score", 0),
            raw_features.get("hesitation_score", 0),
        ]
        max_score = max(scores)
        
        # High anomaly score for extreme values
        if max_score >= 0.9:
            return 0.9
        elif max_score >= 0.8:
            return 0.7
        elif max_score >= 0.7:
            return 0.5
        else:
            return max_score * 0.5
    
    def _detect_single_metric_anomalies(
        self,
        raw_features: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Detect if any single metric is extremely anomalous.
        
        This catches cases like 95% paste with everything else normal.
        """
        anomalies = []
        
        paste_score = raw_features.get("paste_score", 0)
        focus_score = raw_features.get("focus_score", 0)
        hesitation_score = raw_features.get("hesitation_score", 0)
        
        # Get nested paste features for details
        paste_features = raw_features.get("paste", {})
        focus_features = raw_features.get("focus", {})
        
        if paste_score >= 0.85:
            paste_count = paste_features.get("paste_count", 0)
            total_length = paste_features.get("total_paste_length", 0)
            anomalies.append(f"Extreme paste rate: {paste_count} pastes, {total_length} chars")
        
        if focus_score >= 0.7:
            blur_count = focus_features.get("blur_count", 0)
            anomalies.append(f"Excessive tab switching: {blur_count} switches")
        
        if hesitation_score >= 0.8:
            anomalies.append("Unusual hesitation patterns detected")
        
        return len(anomalies) > 0, anomalies
    
    def _get_top_features(
        self,
        raw_features: Dict[str, Any],
        derived: DerivedFeatures
    ) -> List[str]:
        """Get the top contributing features for this prediction."""
        feature_values = {
            "paste_score": raw_features.get("paste_score", 0),
            "focus_score": raw_features.get("focus_score", 0),
            "hesitation_score": raw_features.get("hesitation_score", 0),
            "typing_score": raw_features.get("typing_score", 0),
            "paste_after_blur_ratio": derived.paste_after_blur_ratio,
            "burst_density": min(derived.burst_density / 10, 1.0),
        }
        
        # Sort by value and return top 3
        sorted_features = sorted(
            feature_values.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [f"{name}: {value:.0%}" for name, value in sorted_features[:3] if value > 0.3]
    
    # Train method removed - training is done via train_model.py
    
    def _save_models(self):
        """Save models - legacy support."""
        pass
    
    def _load_models(self):
        """Load trained models from disk."""
        import joblib
        
        rf_path = os.path.join(self.model_path, "rf_model_latest.pkl")
        if_path = os.path.join(self.model_path, "if_model.pkl") # Use IF if exists (optional)
        scaler_path = os.path.join(self.model_path, "scaler_latest.pkl")
        vectorizer_path = os.path.join(self.model_path, "vectorizer_latest.pkl")
        imputer_path = os.path.join(self.model_path, "imputer_latest.pkl")
        
        try:
            if os.path.exists(rf_path):
                self.rf_model = joblib.load(rf_path)
            
            # optional IF
            if os.path.exists(if_path):
                 self.if_model = joblib.load(if_path)
                    
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)

            if os.path.exists(vectorizer_path):
                self.vectorizer = joblib.load(vectorizer_path)
                
            if os.path.exists(imputer_path):
                self.imputer = joblib.load(imputer_path)
            
            self.is_trained = (
                self.rf_model is not None and 
                self.vectorizer is not None
            )
            
            if self.is_trained:
                logger.info(f"ML models loaded from {self.model_path}")
            else:
                logger.warning(f"Could not load ML models from {self.model_path}, using mode: HEURISTIC")
                
        except Exception as e:
            logger.warning(f"Could not load ML models: {e}")
            self.is_trained = False


# Global instance for convenience
_predictor: Optional[MLPredictor] = None


def get_predictor() -> MLPredictor:
    """Get or create the global ML predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = MLPredictor()
    return _predictor


def predict_cheating(
    features: Dict[str, Any],
    events: Optional[List[Dict[str, Any]]] = None,
    session_id: str = ""
) -> MLPrediction:
    """
    Convenience function for ML-based prediction.
    """
    predictor = get_predictor()
    return predictor.predict(features, events, session_id)

