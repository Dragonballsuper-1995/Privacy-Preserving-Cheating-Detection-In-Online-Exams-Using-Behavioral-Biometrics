"""
Explainable AI with SHAP

Provides model interpretability and feature importance explanations.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️ SHAP not installed. Install with: pip install shap")


@dataclass
class Explanation:
    """Explanation for a prediction."""
    session_id: str
    prediction: float
    feature_impacts: Dict[str, float]  # feature_name -> SHAP value
    top_positive_features: List[tuple[str, float]]  # Features increasing risk
    top_negative_features: List[tuple[str, float]]  # Features decreasing risk
    base_value: float  # Expected model output
    explanation_text: str


def explain_prediction(
    model,
    features: Dict[str, Any],
    feature_names: List[str],
    session_id: str = ""
) -> Explanation:
    """
    Generate explanation for a model prediction using SHAP.
    
    Args:
        model: Trained ML model
        features: Feature dictionary
        feature_names: List of feature names
        session_id: Session identifier
        
    Returns:
        Explanation object with SHAP values and human-readable text
    """
    if not SHAP_AVAILABLE:
        # Fallback: simple feature importance
        return _fallback_explanation(features, session_id)
    
    try:
        # Convert features to array
        feature_vector = np.array([features.get(name, 0.0) for name in feature_names]).reshape(1, -1)
        
        # Create SHAP explainer
        explainer = shap.TreeExplainer(model)
        
        # Get SHAP values
        shap_values = explainer.shap_values(feature_vector)
        
        # Handle multi-class output
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Get values for positive class
        
        shap_values = shap_values[0]  # Get first sample
        base_value = explainer.expected_value
        
        if isinstance(base_value, np.ndarray):
            base_value = base_value[1]
        
        # Create feature impact dictionary
        feature_impacts = {}
        for name, value in zip(feature_names, shap_values):
            feature_impacts[name] = float(value)
        
        # Sort features by absolute impact
        sorted_features = sorted(feature_impacts.items(), key=lambda x: abs(x[1]), reverse=True)
        
        # Separate positive and negative impacts
        positive_features = [(name, val) for name, val in sorted_features if val > 0][:5]
        negative_features = [(name, val) for name, val in sorted_features if val < 0][:5]
        
        # Generate explanation text
        explanation_text = _generate_explanation_text(
            positive_features,
            negative_features,
            base_value,
            sum(shap_values)
        )
        
        return Explanation(
            session_id=session_id,
            prediction=base_value + sum(shap_values),
            feature_impacts=feature_impacts,
            top_positive_features=positive_features,
            top_negative_features=negative_features,
            base_value=float(base_value),
            explanation_text=explanation_text
        )
    
    except Exception as e:
        print(f"SHAP explanation failed: {e}")
        return _fallback_explanation(features, session_id)


def _fallback_explanation(features: Dict[str, Any], session_id: str) -> Explanation:
    """
    Fallback explanation when SHAP is not available.
    
    Uses simple heuristics based on feature values.
    """
    # Simple rule-based explanation
    suspicious_features = []
    normal_features = []
    
    # Check for suspicious patterns
    if features.get("paste_count", 0) > 0:
        suspicious_features.append(("paste_count", features["paste_count"]))
    
    if features.get("blur_count", 0) > 3:
        suspicious_features.append(("tab_switching", features["blur_count"]))
    
    if features.get("typing_speed_wpm", 0) > 120:
        suspicious_features.append(("very_fast_typing", features["typing_speed_wpm"]))
    
    # Normal patterns
    if features.get("backspace_ratio", 0) > 0.1:
        normal_features.append(("natural_editing", features["backspace_ratio"]))
    
    explanation_text = "Explanation based on behavioral patterns:\n"
    
    if suspicious_features:
        explanation_text += "\nRisk factors:\n"
        for feature, value in suspicious_features:
            explanation_text += f"- {feature}: {value}\n"
    
    if normal_features:
        explanation_text += "\nNormal behaviors:\n"
        for feature, value in normal_features:
            explanation_text += f"- {feature}: {value}\n"
    
    return Explanation(
        session_id=session_id,
        prediction=0.5,
        feature_impacts={},
        top_positive_features=suspicious_features,
        top_negative_features=normal_features,
        base_value=0.5,
        explanation_text=explanation_text
    )


def _generate_explanation_text(
    positive_features: List[tuple[str, float]],
    negative_features: List[tuple[str, float]],
    base_value: float,
    total_impact: float
) -> str:
    """Generate human-readable explanation text."""
    
    explanation = f"Model Explanation:\n\n"
    explanation += f"Base risk (average student): {base_value:.2%}\n"
    explanation += f"Predicted risk for this session: {(base_value + total_impact):.2%}\n\n"
    
    if positive_features:
        explanation += "Factors increasing risk:\n"
        for name, value in positive_features:
            explanation += f"  • {name}: +{value:.3f} ({_describe_impact(value)})\n"
    
    if negative_features:
        explanation += "\nFactors decreasing risk:\n"
        for name, value in negative_features:
            explanation += f"  • {name}: {value:.3f} ({_describe_impact(value)})\n"
    
    return explanation


def _describe_impact(value: float) -> str:
    """Describe the magnitude of a SHAP value impact."""
    abs_value = abs(value)
    if abs_value > 0.2:
        return "strong impact"
    elif abs_value > 0.1:
        return "moderate impact"
    elif abs_value > 0.05:
        return "small impact"
    else:
        return "minimal impact"


def batch_explain(
    model,
    features_list: List[Dict[str, Any]],
    feature_names: List[str]
) -> List[Explanation]:
    """
    Generate explanations for multiple predictions.
    
    Args:
        model: Trained ML model
        features_list: List of feature dictionaries
        feature_names: List of feature names
        
    Returns:
        List of explanations
    """
    explanations = []
    
    for i, features in enumerate(features_list):
        session_id = features.get("session_id", f"session_{i}")
        explanation = explain_prediction(model, features, feature_names, session_id)
        explanations.append(explanation)
    
    return explanations


def get_global_feature_importance(
    model,
    feature_names: List[str],
    background_data: np.ndarray = None
) -> Dict[str, float]:
    """
    Get global feature importance across all predictions.
    
    Args:
        model: Trained ML model
        feature_names: List of feature names
        background_data: Background dataset for SHAP
        
    Returns:
        Dictionary of feature importances
    """
    if not SHAP_AVAILABLE:
        # Fallback: use model's feature_importances_ if available
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            return dict(zip(feature_names, importances))
        return {}
    
    try:
        explainer = shap.TreeExplainer(model)
        
        if background_data is None:
            # Use a small synthetic background
            background_data = np.zeros((10, len(feature_names)))
        
        shap_values = explainer.shap_values(background_data)
        
        # Handle multi-class
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Calculate mean absolute SHAP value for each feature
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        
        return dict(zip(feature_names, mean_abs_shap))
    
    except Exception as e:
        print(f"Global importance calculation failed: {e}")
        return {}
