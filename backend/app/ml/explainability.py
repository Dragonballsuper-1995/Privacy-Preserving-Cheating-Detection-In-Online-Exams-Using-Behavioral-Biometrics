"""
Explainability Module

Provides feature importance and per-prediction explanations
for the cheating detection models.

Two modes:
1. Model-based (always available): uses sklearn feature_importances_ from
   the trained RandomForest and IsolationForest.
2. SHAP (optional): uses shap>=0.44 for per-sample TreeExplainer values.
   Install with:  pip install 'shap>=0.44.0'
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import logging
import os

import numpy as np

logger = logging.getLogger(__name__)

# Try to import SHAP — it's optional
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


@dataclass
class FeatureExplanation:
    """Explanation for a single prediction."""
    feature_name: str
    importance: float         # model-level importance (0-1)
    contribution: float       # per-sample contribution (SHAP value or approx)
    value: float              # actual feature value for this sample
    direction: str            # "risk" or "safe"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature": self.feature_name,
            "importance": round(self.importance, 4),
            "contribution": round(self.contribution, 4),
            "value": round(self.value, 4),
            "direction": self.direction,
        }


@dataclass
class ExplainabilityResult:
    """Full explanation result for one session."""
    session_id: str
    risk_score: float
    method: str                 # "shap" or "model_importance"
    top_features: List[FeatureExplanation] = field(default_factory=list)
    global_importances: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "risk_score": round(self.risk_score, 4),
            "method": self.method,
            "top_features": [f.to_dict() for f in self.top_features],
            "global_importances": {
                k: round(v, 4)
                for k, v in sorted(
                    self.global_importances.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:15]
            },
        }


# ── Global importance from trained models ──

def get_feature_importance_from_model(
    predictor=None,
) -> Dict[str, float]:
    """
    Extract global feature importances from the trained ML models.

    Works with any sklearn estimator that exposes either
    `feature_importances_` (tree-based) or `coef_` (linear).

    Returns:
        Dict mapping feature name -> importance (0-1, normalized).
    """
    if predictor is None:
        from app.ml.predictor import get_predictor
        predictor = get_predictor()

    if not predictor.is_trained or predictor.rf_model is None:
        return {}

    rf = predictor.rf_model
    vectorizer = predictor.vectorizer

    # Get raw importances
    if hasattr(rf, "feature_importances_"):
        raw = rf.feature_importances_
    elif hasattr(rf, "coef_"):
        raw = np.abs(rf.coef_).flatten()
    else:
        return {}

    # Get feature names from the vectorizer
    if vectorizer is None:
        feature_names = [f"feature_{i}" for i in range(len(raw))]
    elif hasattr(vectorizer, "get_feature_names_out"):
        feature_names = list(vectorizer.get_feature_names_out())
    elif hasattr(vectorizer, "feature_names_"):
        feature_names = list(vectorizer.feature_names_)
    else:
        feature_names = [f"feature_{i}" for i in range(len(raw))]

    if len(feature_names) != len(raw):
        # Mismatch — fall back to indexed names
        feature_names = [f"feature_{i}" for i in range(len(raw))]

    # Normalize to 0-1
    total = raw.sum()
    if total > 0:
        normalized = raw / total
    else:
        normalized = raw

    return dict(zip(feature_names, normalized.tolist()))


# ── Per-sample explanation ──

def explain_prediction(
    raw_features: Dict[str, Any],
    session_id: str = "",
    risk_score: float = 0.0,
    predictor=None,
    top_n: int = 6,
) -> ExplainabilityResult:
    """
    Generate a human-readable explanation for a single prediction.

    Tries SHAP first (if installed); falls back to model importances
    weighted by the sample's feature values.

    Args:
        raw_features: Feature dict (from SessionFeatures.to_dict())
        session_id: Session identifier
        risk_score: Pre-computed risk score
        predictor: Optional MLPredictor instance
        top_n: Number of top features to return

    Returns:
        ExplainabilityResult with ranked feature explanations
    """
    if predictor is None:
        from app.ml.predictor import get_predictor
        predictor = get_predictor()

    global_importances = get_feature_importance_from_model(predictor)

    # Try SHAP first
    if SHAP_AVAILABLE and predictor.is_trained and predictor.rf_model is not None:
        try:
            result = _shap_explanation(
                predictor, raw_features, global_importances,
                session_id, risk_score, top_n,
            )
            if result is not None:
                return result
        except Exception as e:
            logger.warning(f"SHAP explanation failed, using fallback: {e}")

    # Fallback: model importance × sample value
    return _fallback_explanation(
        predictor, raw_features, global_importances,
        session_id, risk_score, top_n,
    )


def _shap_explanation(
    predictor,
    raw_features: Dict[str, Any],
    global_importances: Dict[str, float],
    session_id: str,
    risk_score: float,
    top_n: int,
) -> Optional[ExplainabilityResult]:
    """Generate explanation using SHAP TreeExplainer."""
    from app.ml.derived_features import extract_derived_features

    derived = extract_derived_features(raw_features)
    vector = predictor.features_to_vector(raw_features, derived)
    if vector is None:
        return None

    if predictor.imputer:
        vector = predictor.imputer.transform(vector)
    if predictor.scaler:
        vector = predictor.scaler.transform(vector)

    explainer = shap.TreeExplainer(predictor.rf_model)
    shap_values = explainer.shap_values(vector)

    # shap_values can be [array_class_0, array_class_1] or single array
    if isinstance(shap_values, list):
        # Use class-1 (cheating) SHAP values
        sv = shap_values[1][0]
    else:
        sv = shap_values[0]

    # Get feature names
    if predictor.vectorizer and hasattr(predictor.vectorizer, "get_feature_names_out"):
        names = list(predictor.vectorizer.get_feature_names_out())
    elif predictor.vectorizer and hasattr(predictor.vectorizer, "feature_names_"):
        names = list(predictor.vectorizer.feature_names_)
    else:
        names = [f"feature_{i}" for i in range(len(sv))]

    # Build explanations sorted by |SHAP value|
    indices = np.argsort(np.abs(sv))[::-1][:top_n]
    explanations = []

    # Get actual feature values as a dense array
    v_dense = vector.toarray().flatten() if hasattr(vector, "toarray") else np.asarray(vector).flatten()

    for idx in indices:
        name = names[idx] if idx < len(names) else f"feature_{idx}"
        explanations.append(FeatureExplanation(
            feature_name=name,
            importance=global_importances.get(name, 0.0),
            contribution=float(sv[idx]),
            value=float(v_dense[idx]) if idx < len(v_dense) else 0.0,
            direction="risk" if sv[idx] > 0 else "safe",
        ))

    return ExplainabilityResult(
        session_id=session_id,
        risk_score=risk_score,
        method="shap",
        top_features=explanations,
        global_importances=global_importances,
    )


def _fallback_explanation(
    predictor,
    raw_features: Dict[str, Any],
    global_importances: Dict[str, float],
    session_id: str,
    risk_score: float,
    top_n: int,
) -> ExplainabilityResult:
    """
    Fallback explanation using model importances weighted by feature values.

    For each feature: contribution ≈ importance × value
    This is a reasonable approximation when SHAP is not available.
    """
    from app.ml.derived_features import extract_derived_features

    # Gather feature values from raw_features (use same keys as model)
    derived = extract_derived_features(raw_features)

    # Build a mapping of interpretable feature names → values
    feature_values: Dict[str, float] = {
        "paste_score": float(raw_features.get("paste_score", 0)),
        "focus_score": float(raw_features.get("focus_score", 0)),
        "hesitation_score": float(raw_features.get("hesitation_score", 0)),
        "typing_score": float(raw_features.get("typing_score", 0)),
        "text_score": float(raw_features.get("text_score", 0)),
        "overall_score": float(raw_features.get("overall_score", 0)),
        "paste_after_blur_ratio": derived.paste_after_blur_ratio,
        "burst_density": derived.burst_density,
        "paste_to_typing_ratio": derived.paste_to_typing_ratio,
        "paste_score_amplified": derived.paste_score_amplified,
        "focus_score_amplified": derived.focus_score_amplified,
        "hesitation_score_amplified": derived.hesitation_score_amplified,
    }

    # Also pull nested paste/focus sub-features
    paste = raw_features.get("paste", {})
    if isinstance(paste, dict):
        for k, v in paste.items():
            if isinstance(v, (int, float)):
                feature_values[f"paste_{k}"] = float(v)

    focus = raw_features.get("focus", {})
    if isinstance(focus, dict):
        for k, v in focus.items():
            if isinstance(v, (int, float)):
                feature_values[f"focus_{k}"] = float(v)

    # Compute approximate contributions
    scored: List[Tuple[str, float, float, float]] = []  # (name, importance, contribution, value)

    for name, value in feature_values.items():
        imp = global_importances.get(name, 0.0)
        if imp == 0.0 and global_importances:
            # Try partial match (vectorizer may prefix)
            for gn, gi in global_importances.items():
                if name in gn or gn in name:
                    imp = gi
                    break
        # Fallback: uniform importance
        if imp == 0.0 and not global_importances:
            imp = 1.0 / max(len(feature_values), 1)

        contribution = imp * abs(value)
        scored.append((name, imp, contribution, value))

    # Sort by contribution desc
    scored.sort(key=lambda x: x[2], reverse=True)

    explanations = []
    for name, imp, contrib, value in scored[:top_n]:
        explanations.append(FeatureExplanation(
            feature_name=name,
            importance=imp,
            contribution=contrib,
            value=value,
            direction="risk" if value > 0.3 else "safe",
        ))

    return ExplainabilityResult(
        session_id=session_id,
        risk_score=risk_score,
        method="model_importance",
        top_features=explanations,
        global_importances=global_importances,
    )
