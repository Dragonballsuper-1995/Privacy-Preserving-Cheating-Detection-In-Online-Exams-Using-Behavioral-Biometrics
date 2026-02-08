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
    
    # Feature names in order (must match training)
    FEATURE_NAMES = [
        # Raw scores
        "typing_score",
        "hesitation_score", 
        "paste_score",
        "focus_score",
        "text_score",
        # Derived features
        "paste_after_blur_ratio",
        "burst_density",
        "typing_consistency",
        "paste_to_typing_ratio",
        "absence_concentration",
        # Amplified scores
        "paste_score_amplified",
        "focus_score_amplified",
        "hesitation_score_amplified",
    ]
    
    # Feature importance weights (learned from training or preset)
    FEATURE_IMPORTANCE = {
        "paste_score_amplified": 0.18,
        "paste_after_blur_ratio": 0.16,
        "focus_score_amplified": 0.14,
        "burst_density": 0.12,
        "paste_score": 0.10,
        "focus_score": 0.08,
        "hesitation_score_amplified": 0.07,
        "paste_to_typing_ratio": 0.05,
        "typing_score": 0.04,
        "hesitation_score": 0.03,
        "absence_concentration": 0.02,
        "typing_consistency": 0.01,
        "text_score": 0.00,
    }
    
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
        self.model_path = model_path or os.path.join(settings.models_dir, "ml_predictor")
        
        # Initialize models
        self.rf_model: Optional[RandomForestClassifier] = None
        self.if_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.is_trained = False
        
        # Try to load existing models
        self._load_models()
    
    def features_to_vector(
        self,
        raw_features: Dict[str, Any],
        derived: Optional[DerivedFeatures] = None
    ) -> np.ndarray:
        """
        Convert features to numpy vector for ML models.
        
        Args:
            raw_features: Dictionary from SessionFeatures.to_dict()
            derived: Pre-computed derived features (optional)
            
        Returns:
            Numpy array of feature values
        """
        # Extract derived features if not provided
        if derived is None:
            derived = extract_derived_features(raw_features)
        
        derived_dict = derived.to_dict()
        
        # Build vector in consistent order
        vector = []
        for name in self.FEATURE_NAMES:
            if name in derived_dict:
                vector.append(derived_dict[name])
            else:
                vector.append(raw_features.get(name, 0.0))
        
        return np.array(vector).reshape(1, -1)
    
    def predict(
        self,
        raw_features: Dict[str, Any],
        events: Optional[List[Dict[str, Any]]] = None,
        session_id: str = ""
    ) -> MLPrediction:
        """
        Make ML-based prediction on a session.
        
        Args:
            raw_features: Dictionary from SessionFeatures.to_dict()
            events: Optional list of raw events for burst detection
            session_id: Session identifier
            
        Returns:
            MLPrediction with probability and flags
        """
        # Extract derived features
        derived = extract_derived_features(raw_features, events)
        
        # Convert to vector
        vector = self.features_to_vector(raw_features, derived)
        
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
        
        if self.is_trained and self.rf_model and self.scaler:
            # Use trained models
            scaled = self.scaler.transform(vector)
            
            # Random Forest probability
            try:
                rf_proba = self.rf_model.predict_proba(scaled)
                rf_score = rf_proba[0][1]  # Probability of class 1 (cheating)
            except Exception as e:
                logger.warning(f"RF prediction failed: {e}")
                rf_score = self._heuristic_score(raw_features, derived)
            
            # Isolation Forest anomaly
            if self.if_model:
                try:
                    if_pred = self.if_model.score_samples(scaled)
                    # Convert to 0-1 range (lower IF score = more anomalous)
                    if_score = 1 - (if_pred[0] + 0.5)  # Rough normalization
                    if_score = max(0, min(1, if_score))
                    anomaly_detected = if_pred[0] < -0.3  # Anomaly threshold
                except Exception as e:
                    logger.warning(f"IF prediction failed: {e}")
        else:
            # Use heuristic fallback
            rf_score = self._heuristic_score(raw_features, derived)
            if_score = self._check_extreme_values(raw_features)
            anomaly_detected = if_score > 0.7
        
        # Check for extreme single metrics (always flag these)
        if not anomaly_detected:
            anomaly_detected, anomaly_reasons = self._detect_single_metric_anomalies(raw_features)
        
        # Combine scores
        # Weight: RF 50%, IF 25%, Burst 25%
        combined_score = (
            rf_score * 0.50 +
            if_score * 0.25 +
            burst_bonus * 0.25
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
        
        # Get top contributing features
        top_features = self._get_top_features(raw_features, derived)
        
        return MLPrediction(
            probability=round(final_probability, 3),
            confidence=confidence,
            is_flagged=final_probability >= self.flag_threshold,
            top_features=top_features,
            anomaly_detected=anomaly_detected,
            anomaly_reasons=anomaly_reasons,
            burst_patterns=burst_patterns,
            raw_rf_score=round(rf_score, 3),
            raw_if_score=round(if_score, 3),
            burst_bonus=round(burst_bonus, 3),
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
    
    def train(
        self,
        training_data: List[Tuple[Dict[str, Any], int]],
        save_after: bool = True
    ) -> Dict[str, float]:
        """
        Train the ML models on labeled data.
        
        Args:
            training_data: List of (features_dict, label) tuples
                - features_dict: From SessionFeatures.to_dict()
                - label: 0 (clean) or 1 (cheating)
            save_after: Whether to save models after training
            
        Returns:
            Training metrics (accuracy, etc.)
        """
        if len(training_data) < 10:
            raise ValueError("Need at least 10 samples for training")
        
        # Extract features and labels
        X = []
        y = []
        
        for features, label in training_data:
            derived = extract_derived_features(features)
            vector = self.features_to_vector(features, derived)
            X.append(vector.flatten())
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Initialize scaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest with calibration for better probabilities
        base_rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        self.rf_model = CalibratedClassifierCV(base_rf, cv=3)
        self.rf_model.fit(X_scaled, y)
        
        # Train Isolation Forest on "clean" samples only
        clean_samples = X_scaled[y == 0]
        if len(clean_samples) >= 5:
            self.if_model = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            self.if_model.fit(clean_samples)
        
        self.is_trained = True
        
        # Calculate training accuracy
        predictions = self.rf_model.predict(X_scaled)
        accuracy = (predictions == y).mean()
        
        # Save models
        if save_after:
            self._save_models()
        
        return {
            "accuracy": accuracy,
            "n_samples": len(training_data),
            "n_cheating": int(y.sum()),
            "n_clean": int((y == 0).sum()),
        }
    
    def _save_models(self):
        """Save trained models to disk."""
        os.makedirs(self.model_path, exist_ok=True)
        
        if self.rf_model:
            with open(os.path.join(self.model_path, "rf_model.pkl"), "wb") as f:
                pickle.dump(self.rf_model, f)
        
        if self.if_model:
            with open(os.path.join(self.model_path, "if_model.pkl"), "wb") as f:
                pickle.dump(self.if_model, f)
        
        if self.scaler:
            with open(os.path.join(self.model_path, "scaler.pkl"), "wb") as f:
                pickle.dump(self.scaler, f)
        
        logger.info(f"ML models saved to {self.model_path}")
    
    def _load_models(self):
        """Load trained models from disk."""
        rf_path = os.path.join(self.model_path, "rf_model.pkl")
        if_path = os.path.join(self.model_path, "if_model.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")
        
        try:
            if os.path.exists(rf_path):
                with open(rf_path, "rb") as f:
                    self.rf_model = pickle.load(f)
                    
            if os.path.exists(if_path):
                with open(if_path, "rb") as f:
                    self.if_model = pickle.load(f)
                    
            if os.path.exists(scaler_path):
                with open(scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
            
            self.is_trained = (
                self.rf_model is not None and 
                self.scaler is not None
            )
            
            if self.is_trained:
                logger.info(f"ML models loaded from {self.model_path}")
                
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
    
    Args:
        features: Dictionary from SessionFeatures.to_dict()
        events: Optional raw events for burst detection
        session_id: Session identifier
        
    Returns:
        MLPrediction with probability and flags
    """
    predictor = get_predictor()
    return predictor.predict(features, events, session_id)
