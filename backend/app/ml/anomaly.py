"""
Behavioral Anomaly Detection using Isolation Forest

Detects unusual behavioral patterns that deviate from normal exam-taking behavior.
Uses unsupervised learning to identify outliers without labeled training data.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import numpy as np
import pickle
import os

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.core.config import settings


@dataclass
class AnomalyResult:
    """Result of anomaly detection for a session."""
    session_id: str
    is_anomaly: bool
    anomaly_score: float  # -1 to 1 (more negative = more anomalous)
    normalized_score: float  # 0 to 1 (higher = more anomalous)
    contributing_factors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "is_anomaly": self.is_anomaly,
            "anomaly_score": self.anomaly_score,
            "normalized_score": self.normalized_score,
            "contributing_factors": self.contributing_factors,
        }


class BehaviorAnomalyDetector:
    """
    Detects anomalous behavioral patterns using Isolation Forest.
    
    Features used for anomaly detection:
    - Keystroke dynamics (typing speed, inter-key delays)
    - Hesitation patterns (pause count, duration)
    - Paste behavior (paste count, timing)
    - Focus patterns (blur count, unfocused time)
    """
    
    FEATURE_NAMES = [
        "mean_inter_key_delay",
        "std_inter_key_delay",
        "typing_speed_wpm",
        "pause_count",
        "max_pause_duration",
        "pause_ratio",
        "paste_count",
        "total_paste_length",
        "paste_after_blur",
        "blur_count",
        "total_unfocused_time",
        "unfocused_ratio",
    ]
    
    def __init__(
        self,
        contamination: float = 0.1,
        model_path: Optional[str] = None
    ):
        """
        Initialize the anomaly detector.
        
        Args:
            contamination: Expected proportion of outliers (0.1 = 10%)
            model_path: Path to load/save trained model
        """
        self.contamination = contamination
        self.model_path = model_path or os.path.join(settings.models_dir, "anomaly_detector.pkl")
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        self._is_fitted = False
    
    def features_to_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Convert feature dictionary to numpy vector.
        
        Args:
            features: Dictionary from SessionFeatures.to_dict()
            
        Returns:
            Numpy array of feature values
        """
        # Extract features from nested structure
        keystroke = features.get("keystroke", {})
        hesitation = features.get("hesitation", {})
        paste = features.get("paste", {})
        focus = features.get("focus", {})
        
        vector = np.array([
            keystroke.get("mean_inter_key_delay", 0),
            keystroke.get("std_inter_key_delay", 0),
            keystroke.get("typing_speed_wpm", 0),
            hesitation.get("pause_count", 0),
            hesitation.get("max_pause_duration", 0),
            hesitation.get("pause_ratio", 0),
            paste.get("paste_count", 0),
            paste.get("total_paste_length", 0),
            paste.get("paste_after_blur", 0),
            focus.get("blur_count", 0),
            focus.get("total_unfocused_time", 0),
            focus.get("unfocused_ratio", 0),
        ])
        
        return vector
    
    def fit(self, feature_vectors: List[Dict[str, Any]]):
        """
        Fit the anomaly detector on a set of baseline sessions.
        
        Args:
            feature_vectors: List of feature dictionaries from normal sessions
        """
        if not feature_vectors:
            return
        
        # Convert to numpy array
        X = np.array([self.features_to_vector(f) for f in feature_vectors])
        
        # Fit scaler and model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self._is_fitted = True
        
        # Save model
        self.save()
    
    def detect(self, features: Dict[str, Any], session_id: str = "") -> AnomalyResult:
        """
        Detect if a session's behavior is anomalous.
        
        Args:
            features: Feature dictionary from SessionFeatures.to_dict()
            session_id: Session identifier
            
        Returns:
            AnomalyResult with detection results
        """
        vector = self.features_to_vector(features)
        
        if not self._is_fitted:
            # Use heuristic-based detection if model not trained
            return self._heuristic_detection(vector, features, session_id)
        
        # Scale features
        vector_scaled = self.scaler.transform(vector.reshape(1, -1))
        
        # Get anomaly score (-1 = anomaly, 1 = normal)
        raw_score = self.model.decision_function(vector_scaled)[0]
        prediction = self.model.predict(vector_scaled)[0]
        
        # Normalize score to 0-1 (higher = more anomalous)
        normalized_score = max(0, min(1, (1 - raw_score) / 2))
        
        # Identify contributing factors
        factors = self._identify_factors(vector, features)
        
        return AnomalyResult(
            session_id=session_id,
            is_anomaly=prediction == -1,
            anomaly_score=float(raw_score),
            normalized_score=normalized_score,
            contributing_factors=factors,
        )
    
    def _heuristic_detection(
        self, 
        vector: np.ndarray, 
        features: Dict[str, Any],
        session_id: str
    ) -> AnomalyResult:
        """
        Fallback heuristic-based anomaly detection.
        
        Used when the model hasn't been trained on baseline data.
        """
        score = 0.0
        factors = []
        
        keystroke = features.get("keystroke", {})
        hesitation = features.get("hesitation", {})
        paste = features.get("paste", {})
        focus = features.get("focus", {})
        
        # Very fast typing
        if keystroke.get("typing_speed_wpm", 0) > 120:
            score += 0.2
            factors.append("unusually_fast_typing")
        
        # High variability in typing rhythm
        if keystroke.get("std_inter_key_delay", 0) > 500:
            score += 0.15
            factors.append("erratic_typing_rhythm")
        
        # Many long pauses
        if hesitation.get("pause_count", 0) >= 5:
            score += 0.15
            if hesitation.get("max_pause_duration", 0) > 30000:
                score += 0.1
                factors.append("extended_pauses")
        
        # Any paste events
        if paste.get("paste_count", 0) > 0:
            score += 0.2
            factors.append("paste_detected")
            if paste.get("paste_after_blur", 0) > 0:
                score += 0.1
                factors.append("paste_after_tab_switch")
        
        # Tab switching
        if focus.get("blur_count", 0) >= 3:
            score += 0.15
            factors.append("frequent_tab_switching")
        
        normalized_score = min(1.0, score)
        
        return AnomalyResult(
            session_id=session_id,
            is_anomaly=normalized_score >= 0.5,
            anomaly_score=1 - 2 * normalized_score,  # Convert to -1 to 1 range
            normalized_score=normalized_score,
            contributing_factors=factors,
        )
    
    def _identify_factors(self, vector: np.ndarray, features: Dict[str, Any]) -> List[str]:
        """Identify which features are contributing to anomaly score."""
        factors = []
        
        keystroke = features.get("keystroke", {})
        hesitation = features.get("hesitation", {})
        paste = features.get("paste", {})
        focus = features.get("focus", {})
        
        # Check each feature against thresholds
        if keystroke.get("typing_speed_wpm", 0) > 100:
            factors.append("high_typing_speed")
        if keystroke.get("std_inter_key_delay", 0) > 400:
            factors.append("variable_typing_rhythm")
        if hesitation.get("pause_ratio", 0) > 0.3:
            factors.append("high_pause_ratio")
        if paste.get("paste_count", 0) > 0:
            factors.append("content_pasted")
        if focus.get("blur_count", 0) > 2:
            factors.append("tab_switching")
        
        return factors
    
    def save(self):
        """Save the trained model to disk."""
        if self._is_fitted:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    "model": self.model,
                    "scaler": self.scaler,
                }, f)
    
    def load(self) -> bool:
        """Load a trained model from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data["model"]
                    self.scaler = data["scaler"]
                    self._is_fitted = True
                return True
            except Exception:
                return False
        return False


def detect_anomalies(
    features: Dict[str, Any], 
    session_id: str = ""
) -> AnomalyResult:
    """
    Convenience function to detect anomalies in a session.
    
    Args:
        features: Feature dictionary from SessionFeatures.to_dict()
        session_id: Session identifier
        
    Returns:
        AnomalyResult with detection results
    """
    detector = BehaviorAnomalyDetector()
    detector.load()  # Try to load trained model
    return detector.detect(features, session_id)
