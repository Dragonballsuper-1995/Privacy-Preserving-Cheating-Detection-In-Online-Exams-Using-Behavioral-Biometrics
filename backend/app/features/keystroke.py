"""
Keystroke Dynamics Feature Extraction

Extracts features related to typing patterns:
- Inter-key delays (time between consecutive keystrokes)
- Key hold times (dwell time)
- Typing speed (WPM)
- Typing rhythm variability
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import statistics


@dataclass
class KeystrokeFeatures:
    """Features extracted from keystroke dynamics."""
    # Inter-key timing
    mean_inter_key_delay: float = 0.0
    std_inter_key_delay: float = 0.0
    min_inter_key_delay: float = 0.0
    max_inter_key_delay: float = 0.0
    median_inter_key_delay: float = 0.0
    
    # Typing speed
    typing_speed_wpm: float = 0.0
    total_keystrokes: int = 0
    
    # Hold times (dwell time)
    mean_hold_time: float = 0.0
    std_hold_time: float = 0.0
    
    # Rhythm variability
    rhythm_variance: float = 0.0
    
    # Special keys
    backspace_count: int = 0
    enter_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mean_inter_key_delay": self.mean_inter_key_delay,
            "std_inter_key_delay": self.std_inter_key_delay,
            "min_inter_key_delay": self.min_inter_key_delay,
            "max_inter_key_delay": self.max_inter_key_delay,
            "median_inter_key_delay": self.median_inter_key_delay,
            "typing_speed_wpm": self.typing_speed_wpm,
            "total_keystrokes": self.total_keystrokes,
            "mean_hold_time": self.mean_hold_time,
            "std_hold_time": self.std_hold_time,
            "rhythm_variance": self.rhythm_variance,
            "backspace_count": self.backspace_count,
            "enter_count": self.enter_count,
        }


def extract_keystroke_features(events: List[Dict[str, Any]]) -> KeystrokeFeatures:
    """
    Extract keystroke dynamics features from raw key events.
    
    Args:
        events: List of event dictionaries with type, data, and timestamp
        
    Returns:
        KeystrokeFeatures dataclass with extracted features
    """
    features = KeystrokeFeatures()
    
    # Filter for key events only
    key_events = [e for e in events if e.get("event_type") == "key"]
    
    if not key_events:
        return features
    
    # Separate keydown and keyup events
    keydown_events = []
    keyup_events = []
    
    for event in key_events:
        data = event.get("data", {})
        event_type = data.get("type", "")
        timestamp = event.get("timestamp", 0)
        key = data.get("key", "")
        
        if event_type == "keydown":
            keydown_events.append({
                "timestamp": timestamp,
                "key": key,
                "code": data.get("code", "")
            })
        elif event_type == "keyup":
            keyup_events.append({
                "timestamp": timestamp,
                "key": key,
                "code": data.get("code", "")
            })
    
    # Sort by timestamp
    keydown_events.sort(key=lambda x: x["timestamp"])
    keyup_events.sort(key=lambda x: x["timestamp"])
    
    features.total_keystrokes = len(keydown_events)
    
    # Calculate inter-key delays (flight time between consecutive keydowns)
    inter_key_delays = []
    for i in range(1, len(keydown_events)):
        delay = keydown_events[i]["timestamp"] - keydown_events[i-1]["timestamp"]
        # Filter out unreasonably long delays (> 30 seconds = likely a break)
        if 0 < delay < 30000:
            inter_key_delays.append(delay)
    
    if inter_key_delays:
        features.mean_inter_key_delay = statistics.mean(inter_key_delays)
        features.std_inter_key_delay = statistics.stdev(inter_key_delays) if len(inter_key_delays) > 1 else 0
        features.min_inter_key_delay = min(inter_key_delays)
        features.max_inter_key_delay = max(inter_key_delays)
        features.median_inter_key_delay = statistics.median(inter_key_delays)
        features.rhythm_variance = statistics.variance(inter_key_delays) if len(inter_key_delays) > 1 else 0
    
    # Calculate hold times (dwell time = keyup - keydown for same key)
    hold_times = []
    keydown_map = {}  # Map key -> timestamp of last keydown
    
    for event in keydown_events:
        keydown_map[event["code"]] = event["timestamp"]
    
    for event in keyup_events:
        code = event["code"]
        if code in keydown_map:
            hold_time = event["timestamp"] - keydown_map[code]
            if 0 < hold_time < 2000:  # Filter unreasonable hold times
                hold_times.append(hold_time)
    
    if hold_times:
        features.mean_hold_time = statistics.mean(hold_times)
        features.std_hold_time = statistics.stdev(hold_times) if len(hold_times) > 1 else 0
    
    # Calculate typing speed (WPM)
    if len(keydown_events) >= 2:
        total_time_ms = keydown_events[-1]["timestamp"] - keydown_events[0]["timestamp"]
        total_time_minutes = total_time_ms / 1000 / 60
        
        if total_time_minutes > 0:
            # Approximate words = keystrokes / 5
            words = features.total_keystrokes / 5
            features.typing_speed_wpm = words / total_time_minutes
    
    # Count special keys
    for event in keydown_events:
        key = event.get("key", "")
        if key == "Backspace":
            features.backspace_count += 1
        elif key == "Enter":
            features.enter_count += 1
    
    return features


def calculate_anomaly_score(features: KeystrokeFeatures, baseline: KeystrokeFeatures = None) -> float:
    """
    Calculate an anomaly score based on keystroke features.
    
    Higher scores indicate more anomalous (potentially suspicious) behavior.
    
    Args:
        features: Current session's keystroke features
        baseline: Optional baseline for comparison (e.g., average honest user)
        
    Returns:
        Anomaly score between 0 and 1
    """
    score = 0.0
    
    # Very high typing speed might indicate pasting or automated input
    if features.typing_speed_wpm > 120:
        score += 0.3
    elif features.typing_speed_wpm > 80:
        score += 0.1
    
    # High standard deviation in inter-key delay suggests erratic typing
    # (could be switching between typing and looking up answers)
    if features.std_inter_key_delay > 500:
        score += 0.2
    elif features.std_inter_key_delay > 300:
        score += 0.1
    
    # Very consistent rhythm (low variance) could indicate robotic/automated input
    if features.rhythm_variance < 100 and features.total_keystrokes > 50:
        score += 0.15
    
    # High backspace ratio might indicate nervousness or copying errors
    if features.total_keystrokes > 0:
        backspace_ratio = features.backspace_count / features.total_keystrokes
        if backspace_ratio > 0.3:
            score += 0.2
        elif backspace_ratio > 0.2:
            score += 0.1
    
    return min(score, 1.0)
