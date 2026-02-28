import numpy as np
from scipy.stats import ks_2samp
from typing import Dict, Any, List
from sqlalchemy.orm import Session as DBSession
from app.models.session import Session as SessionModel

def calculate_data_drift(reference_data: List[float], current_data: List[float]) -> Dict[str, Any]:
    """Calculate Kolmogorov-Smirnov test for data drift."""
    if not reference_data or not current_data:
        return {"drift_detected": False, "p_value": 1.0, "statistic": 0.0, "message": "Insufficient data"}
    
    # 2-sample KS test
    statistic, p_value = ks_2samp(reference_data, current_data)
    
    # Threshold for drift (e.g., p < 0.05 implies distributions are different)
    drift_detected = p_value < 0.05
    
    return {
        "drift_detected": bool(drift_detected),
        "p_value": float(p_value),
        "statistic": float(statistic),
    }

def _get_feature_drift(features_to_monitor: List[str], reference_sessions: List[SessionModel], current_sessions: List[SessionModel]) -> Dict[str, Any]:
    """Helper to calculate drift across multiple features."""
    drift_metrics = {}
    any_drift = False
    
    for feature in features_to_monitor:
        def get_feature(s):
            if not s.risk_scores:
                return None
            score = s.risk_scores[-1]
            return getattr(score, feature, None)

        ref_values = [get_feature(s) or 0.0 for s in reference_sessions if get_feature(s) is not None]
        curr_values = [get_feature(s) or 0.0 for s in current_sessions if get_feature(s) is not None]
        
        result = calculate_data_drift(ref_values, curr_values)
        drift_metrics[feature] = result
        
        if result.get("drift_detected"):
            any_drift = True
            
    return drift_metrics, any_drift

def _calculate_precision_estimate(reviewed_sessions: List[SessionModel]) -> float:
    """Helper to calculate model precision based on manual reviews."""
    if not reviewed_sessions:
        return 1.0
        
    tp = sum(1 for s in reviewed_sessions if s.is_flagged and s.review_status == 'confirmed_cheating')
    fp = sum(1 for s in reviewed_sessions if s.is_flagged and s.review_status == 'false_positive')
    
    if (tp + fp) > 0:
        return tp / (tp + fp)
    return 1.0

def get_model_health_metrics(db: DBSession) -> Dict[str, Any]:
    """Analyze recent sessions to detect potential distribution shifts."""
    all_sessions = db.query(SessionModel).order_by(SessionModel.created_at).all()
    
    if len(all_sessions) < 20:
        return {
            "status": "insufficient_data",
            "message": "Not enough sessions to calculate drift (need at least 20).",
            "metrics": {}
        }
    
    midpoint = len(all_sessions) // 2
    reference_sessions = all_sessions[:midpoint]
    current_sessions = all_sessions[midpoint:]
    
    features_to_monitor = ['focus_score', 'similarity_score', 'paste_score']
    drift_metrics, any_drift = _get_feature_drift(features_to_monitor, reference_sessions, current_sessions)
            
    reviewed_sessions = [s for s in all_sessions if s.review_status is not None and s.review_status != 'pending']
    accuracy = _calculate_precision_estimate(reviewed_sessions)
        
    return {
        "status": "needs_retraining" if any_drift else "healthy",
        "message": "Data drift detected in one or more features." if any_drift else "Model serving distributions match reference.",
        "metrics": drift_metrics,
        "precision_estimate": float(accuracy),
        "total_sessions": len(all_sessions),
        "reviewed_sessions_count": len(reviewed_sessions)
    }
