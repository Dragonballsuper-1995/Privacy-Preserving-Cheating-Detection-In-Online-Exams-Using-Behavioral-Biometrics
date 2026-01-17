"""
Focus/Blur Event Feature Extraction

Extracts features related to window focus:
- Tab switching frequency
- Time spent unfocused
- Blur-before-action patterns
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class FocusFeatures:
    """Features extracted from focus/blur patterns."""
    # Basic metrics
    blur_count: int = 0
    focus_count: int = 0
    
    # Time analysis
    total_unfocused_time: float = 0.0
    mean_unfocused_duration: float = 0.0
    max_unfocused_duration: float = 0.0
    
    # Patterns
    blur_frequency: float = 0.0  # Blurs per minute
    unfocused_ratio: float = 0.0  # % of time unfocused
    
    # Quick switches (focus returned within 3 seconds - likely accidental)
    quick_switches: int = 0
    
    # Extended absences (> 30 seconds - suspicious)
    extended_absences: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "blur_count": self.blur_count,
            "focus_count": self.focus_count,
            "total_unfocused_time": self.total_unfocused_time,
            "mean_unfocused_duration": self.mean_unfocused_duration,
            "max_unfocused_duration": self.max_unfocused_duration,
            "blur_frequency": self.blur_frequency,
            "unfocused_ratio": self.unfocused_ratio,
            "quick_switches": self.quick_switches,
            "extended_absences": self.extended_absences,
        }


def extract_focus_features(events: List[Dict[str, Any]]) -> FocusFeatures:
    """
    Extract focus/blur behavior features from events.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        FocusFeatures dataclass with extracted features
    """
    features = FocusFeatures()
    
    if not events:
        return features
    
    sorted_events = sorted(events, key=lambda x: x.get("timestamp", 0))
    
    # Get focus events
    focus_events = [
        e for e in sorted_events 
        if e.get("event_type") == "focus"
    ]
    
    if not focus_events:
        return features
    
    # Separate blur and focus events
    blur_events = []
    return_focus_events = []
    
    for event in focus_events:
        event_type = event.get("data", {}).get("type", "")
        timestamp = event.get("timestamp", 0)
        
        if event_type == "blur":
            blur_events.append(timestamp)
        elif event_type == "focus":
            return_focus_events.append(timestamp)
    
    features.blur_count = len(blur_events)
    features.focus_count = len(return_focus_events)
    
    # Calculate unfocused durations (time between blur and next focus)
    unfocused_durations = []
    
    for blur_time in blur_events:
        # Find next focus event after this blur
        next_focus = None
        for focus_time in return_focus_events:
            if focus_time > blur_time:
                next_focus = focus_time
                break
        
        if next_focus:
            duration = next_focus - blur_time
            unfocused_durations.append(duration)
            
            # Categorize
            if duration < 3000:
                features.quick_switches += 1
            elif duration > 30000:
                features.extended_absences += 1
    
    if unfocused_durations:
        features.total_unfocused_time = sum(unfocused_durations)
        features.mean_unfocused_duration = sum(unfocused_durations) / len(unfocused_durations)
        features.max_unfocused_duration = max(unfocused_durations)
    
    # Calculate frequency and ratio
    first_timestamp = sorted_events[0].get("timestamp", 0)
    last_timestamp = sorted_events[-1].get("timestamp", 0)
    total_time = last_timestamp - first_timestamp
    
    if total_time > 0:
        total_time_minutes = total_time / 1000 / 60
        features.blur_frequency = features.blur_count / total_time_minutes if total_time_minutes > 0 else 0
        features.unfocused_ratio = features.total_unfocused_time / total_time
    
    return features


def calculate_focus_score(features: FocusFeatures) -> float:
    """
    Calculate a suspicion score based on focus/blur patterns.
    
    Higher scores indicate more suspicious tab-switching behavior.
    
    Args:
        features: Focus features
        
    Returns:
        Score between 0 and 1
    """
    score = 0.0
    
    # Any tab switching is somewhat suspicious
    if features.blur_count > 0:
        score += 0.05
    
    # Multiple tab switches
    if features.blur_count >= 10:
        score += 0.3
    elif features.blur_count >= 5:
        score += 0.2
    elif features.blur_count >= 3:
        score += 0.1
    
    # Extended absences (> 30 seconds)
    if features.extended_absences >= 3:
        score += 0.3
    elif features.extended_absences >= 1:
        score += 0.15
    
    # Very long single absence
    if features.max_unfocused_duration > 120000:  # > 2 minutes
        score += 0.25
    elif features.max_unfocused_duration > 60000:  # > 1 minute
        score += 0.15
    
    # High unfocused ratio
    if features.unfocused_ratio > 0.3:
        score += 0.2
    elif features.unfocused_ratio > 0.15:
        score += 0.1
    
    return min(score, 1.0)
