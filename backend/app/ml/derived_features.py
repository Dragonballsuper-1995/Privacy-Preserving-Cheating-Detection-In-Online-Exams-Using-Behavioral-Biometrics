"""
Derived Feature Engineering Module

Creates advanced features from raw behavioral data for ML-based detection.
These features capture complex relationships between behaviors.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class DerivedFeatures:
    """Advanced derived features for ML classification."""
    
    # Correlation features
    paste_after_blur_ratio: float = 0.0  # Paste events following blur / total pastes
    
    # Density features  
    burst_density: float = 0.0  # (blur + paste) events per minute
    
    # Consistency features
    typing_consistency: float = 0.0  # 1 - (std_delay / mean_delay)
    
    # Ratio features
    paste_to_typing_ratio: float = 0.0  # Pasted chars / typed chars
    
    # Concentration features
    absence_concentration: float = 0.0  # Max absence / total absence time
    
    # Amplified scores (non-linear boost for extreme values)
    paste_score_amplified: float = 0.0
    focus_score_amplified: float = 0.0
    hesitation_score_amplified: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for ML input."""
        return {
            "paste_after_blur_ratio": self.paste_after_blur_ratio,
            "burst_density": self.burst_density,
            "typing_consistency": self.typing_consistency,
            "paste_to_typing_ratio": self.paste_to_typing_ratio,
            "absence_concentration": self.absence_concentration,
            "paste_score_amplified": self.paste_score_amplified,
            "focus_score_amplified": self.focus_score_amplified,
            "hesitation_score_amplified": self.hesitation_score_amplified,
        }


def amplifier(score: float) -> float:
    """
    Non-linear amplifier for extreme scores.
    
    A 90% score is more than 1.5x worse than 60%.
    This helps the ML model weight extreme behaviors more heavily.
    """
    if score >= 0.8:
        return 1.5  # Extreme behavior - major boost
    elif score >= 0.6:
        return 1.2  # High behavior - moderate boost
    else:
        return 1.0  # Normal range


def extract_derived_features(
    raw_features: Dict[str, Any],
    events: Optional[List[Dict[str, Any]]] = None
) -> DerivedFeatures:
    """
    Extract derived features from raw behavioral features.
    
    Args:
        raw_features: Dictionary from SessionFeatures.to_dict()
        events: Optional list of raw events for temporal analysis
        
    Returns:
        DerivedFeatures with all computed values
    """
    derived = DerivedFeatures()
    
    # Extract nested features
    paste_features = raw_features.get("paste", {})
    focus_features = raw_features.get("focus", {})
    keystroke_features = raw_features.get("keystroke", {})
    hesitation_features = raw_features.get("hesitation", {})
    
    # 1. Paste after blur ratio
    paste_after_blur = paste_features.get("paste_after_blur_count", 0)
    total_pastes = paste_features.get("paste_count", 0)
    if total_pastes > 0:
        derived.paste_after_blur_ratio = paste_after_blur / total_pastes
    
    # 2. Burst density (events per minute)
    session_duration_ms = raw_features.get("session_duration", 60000)  # Default 1 min
    session_duration_min = max(session_duration_ms / 60000, 0.1)  # Avoid division by zero
    
    blur_count = focus_features.get("blur_count", 0)
    paste_count = paste_features.get("paste_count", 0)
    derived.burst_density = (blur_count + paste_count) / session_duration_min
    
    # 3. Typing consistency
    mean_delay = keystroke_features.get("mean_inter_key_delay", 0)
    std_delay = keystroke_features.get("std_inter_key_delay", 0)
    if mean_delay > 0:
        # Higher value = more consistent typing
        derived.typing_consistency = max(0, 1 - (std_delay / mean_delay))
    
    # 4. Paste to typing ratio
    total_paste_length = paste_features.get("total_paste_length", 0)
    total_chars_typed = keystroke_features.get("total_chars_typed", 0)
    total_content = total_paste_length + total_chars_typed
    if total_content > 0:
        derived.paste_to_typing_ratio = total_paste_length / total_content
    
    # 5. Absence concentration  
    max_absence = focus_features.get("max_absence_duration", 0)
    total_absence = focus_features.get("total_absence_time", 0)
    if total_absence > 0:
        derived.absence_concentration = max_absence / total_absence
    
    # 6. Amplified scores (non-linear boosting)
    paste_score = raw_features.get("paste_score", 0)
    focus_score = raw_features.get("focus_score", 0)
    hesitation_score = raw_features.get("hesitation_score", 0)
    
    derived.paste_score_amplified = paste_score * amplifier(paste_score)
    derived.focus_score_amplified = focus_score * amplifier(focus_score)
    derived.hesitation_score_amplified = hesitation_score * amplifier(hesitation_score)
    
    return derived


def detect_bursts(
    events: List[Dict[str, Any]],
    window_ms: int = 5000
) -> List[Dict[str, Any]]:
    """
    Detect temporal burst patterns in events.
    
    Looks for suspicious patterns like:
    - Blur followed by paste within window
    - Multiple blurs followed by large paste
    
    Args:
        events: List of event dictionaries with 'type' and 'timestamp'
        window_ms: Time window in milliseconds
        
    Returns:
        List of detected burst patterns with type and boost value
    """
    bursts = []
    
    # Sort events by timestamp
    sorted_events = sorted(events, key=lambda e: e.get("timestamp", 0))
    
    for i, event in enumerate(sorted_events):
        event_type = event.get("type", "")
        event_time = event.get("timestamp", 0)
        
        # Pattern 1: Blur -> Paste (copy-paste burst)
        if event_type == "paste":
            # Look back for recent blur
            for j in range(i - 1, max(0, i - 10), -1):
                prev_event = sorted_events[j]
                if prev_event.get("type") == "blur":
                    time_diff = event_time - prev_event.get("timestamp", 0)
                    if 0 < time_diff <= window_ms:
                        bursts.append({
                            "type": "copy_paste_burst",
                            "boost": 0.15,
                            "description": f"Paste {time_diff}ms after tab switch"
                        })
                        break
        
        # Pattern 2: Tab switch storm (>5 blurs in 60 seconds)
        if event_type == "blur":
            recent_blurs = 0
            for j in range(max(0, i - 20), i + 1):
                check_event = sorted_events[j]
                if check_event.get("type") == "blur":
                    time_diff = event_time - check_event.get("timestamp", 0)
                    if 0 <= time_diff <= 60000:
                        recent_blurs += 1
            
            if recent_blurs >= 5:
                # Only add once per storm (check if already detected recently)
                if not any(b.get("type") == "tab_switch_storm" for b in bursts[-3:]):
                    bursts.append({
                        "type": "tab_switch_storm",
                        "boost": 0.12,
                        "description": f"{recent_blurs} tab switches in 60 seconds"
                    })
    
    return bursts


def compute_burst_bonus(events: List[Dict[str, Any]]) -> float:
    """
    Compute total burst bonus from event patterns.
    
    Args:
        events: List of session events
        
    Returns:
        Total boost value from detected bursts (0.0 to 0.5)
    """
    bursts = detect_bursts(events)
    total_boost = sum(b.get("boost", 0) for b in bursts)
    return min(0.5, total_boost)  # Cap at 0.5
