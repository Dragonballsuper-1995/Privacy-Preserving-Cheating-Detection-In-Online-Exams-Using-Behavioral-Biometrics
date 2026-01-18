"""
Temporal Consistency Analysis

Analyzes behavior consistency over time:
- Typing speed variance throughout exam
- Behavioral drift (sudden changes in patterns)
- Session clustering (grouping time windows by similarity)
- Anomaly timeline (detecting when suspicious events occur)
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import statistics
import math


@dataclass
class TemporalFeatures:
    """Features related to temporal consistency."""
    # Typing speed consistency
    typing_speed_variance: float = 0.0
    typing_speed_drift: float = 0.0  # Change from start to end
    
    # Behavioral consistency
    behavior_variance_score: float = 0.0
    sudden_change_count: int = 0  # Number of abrupt behavioral shifts
    
    # Time windows
    total_time_windows: int = 0
    consistent_windows: int = 0
    inconsistent_windows: int = 0
    
    # Anomaly timeline
    anomaly_clusters: int = 0  # Groups of anomalies close in time
    peak_anomaly_time: float = 0.0  # Timestamp of highest anomaly concentration
    
    # Focus consistency
    focus_pattern_changes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "typing_speed_variance": self.typing_speed_variance,
            "typing_speed_drift": self.typing_speed_drift,
            "behavior_variance_score": self.behavior_variance_score,
            "sudden_change_count": self.sudden_change_count,
            "total_time_windows": self.total_time_windows,
            "consistent_windows": self.consistent_windows,
            "inconsistent_windows": self.inconsistent_windows,
            "anomaly_clusters": self.anomaly_clusters,
            "peak_anomaly_time": self.peak_anomaly_time,
            "focus_pattern_changes": self.focus_pattern_changes,
        }


def split_into_time_windows(
    events: List[Dict[str, Any]],
    window_size_ms: int = 60000  # 1 minute windows
) -> List[List[Dict[str, Any]]]:
    """Split events into fixed-size time windows."""
    if not events:
        return []
    
    # Sort events by timestamp
    sorted_events = sorted(events, key=lambda x: x.get("timestamp", 0))
    
    if not sorted_events:
        return []
    
    windows = []
    start_time = sorted_events[0]["timestamp"]
    end_time = sorted_events[-1]["timestamp"]
    
    current_window_start = start_time
    
    while current_window_start < end_time:
        window_end = current_window_start + window_size_ms
        
        # Get events in this window
        window_events = [
            e for e in sorted_events
            if current_window_start <= e.get("timestamp", 0) < window_end
        ]
        
        if window_events:
            windows.append(window_events)
        
        current_window_start = window_end
    
    return windows


def calculate_window_typing_speed(events: List[Dict[str, Any]]) -> float:
    """Calculate typing speed for a time window."""
    key_events = [e for e in events if e.get("event_type") == "key"]
    
    if len(key_events) < 2:
        return 0.0
    
    time_span_ms = key_events[-1]["timestamp"] - key_events[0]["timestamp"]
    if time_span_ms <= 0:
        return 0.0
    
    # Convert to words per minute (assuming 5 chars per word)
    words = len(key_events) / 5
    minutes = time_span_ms / 1000 / 60
    
    return words / minutes if minutes > 0 else 0.0


def detect_behavioral_drift(window_features: List[Dict[str, float]], threshold: float = 2.0) -> int:
    """
    Detect sudden changes in behavior between consecutive windows.
    
    Returns count of significant behavioral shifts.
    """
    if len(window_features) < 2:
        return 0
    
    shifts = 0
    
    for i in range(1, len(window_features)):
        prev = window_features[i-1]
        curr = window_features[i]
        
        # Compare key metrics
        changes = []
        
        for key in prev:
            if key in curr:
                prev_val = prev[key]
                curr_val = curr[key]
                
                # Calculate relative change
                if prev_val != 0:
                    relative_change = abs((curr_val - prev_val) / prev_val)
                    changes.append(relative_change)
        
        # If average change is above threshold, count as a shift
        if changes and statistics.mean(changes) > threshold:
            shifts += 1
    
    return shifts


def extract_temporal_features(
    events: List[Dict[str, Any]],
    window_size_ms: int = 60000
) -> TemporalFeatures:
    """
    Extract temporal consistency features from events.
    
    Args:
        events: List of event dictionaries
        window_size_ms: Size of time windows in milliseconds
        
    Returns:
        TemporalFeatures dataclass with extracted features
    """
    features = TemporalFeatures()
    
    if not events:
        return features
    
    # Split into time windows
    windows = split_into_time_windows(events, window_size_ms)
    features.total_time_windows = len(windows)
    
    if len(windows) < 2:
        return features
    
    # Calculate typing speed for each window
    typing_speeds = []
    window_features_list = []
    
    for window in windows:
        typing_speed = calculate_window_typing_speed(window)
        typing_speeds.append(typing_speed)
        
        # Extract simple features for each window
        key_count = len([e for e in window if e.get("event_type") == "key"])
        paste_count = len([e for e in window if e.get("event_type") == "paste"])
        blur_count = len([e for e in window if e.get("event_type") == "blur"])
        
        window_features_list.append({
            "typing_speed": typing_speed,
            "key_count": key_count,
            "paste_count": paste_count,
            "blur_count": blur_count,
        })
    
    # Analyze typing speed variance
    valid_speeds = [s for s in typing_speeds if s > 0]
    if len(valid_speeds) > 1:
        features.typing_speed_variance = statistics.variance(valid_speeds)
        
        # Calculate drift (difference between first and last windows)
        if valid_speeds:
            features.typing_speed_drift = abs(valid_speeds[-1] - valid_speeds[0])
    
    # Detect behavioral shifts
    features.sudden_change_count = detect_behavioral_drift(window_features_list)
    
    # Calculate behavior variance score
    # High variance across windows = inconsistent behavior
    if len(window_features_list) > 1:
        variances = []
        
        for key in ["key_count", "paste_count", "blur_count"]:
            values = [w[key] for w in window_features_list]
            if len(values) > 1 and any(v > 0 for v in values):
                try:
                    variances.append(statistics.variance(values))
                except:
                    pass
        
        if variances:
            features.behavior_variance_score = statistics.mean(variances)
    
    # Classify windows as consistent or inconsistent
    # Use typing speed as primary metric
    if valid_speeds:
        avg_speed = statistics.mean(valid_speeds)
        std_speed = statistics.stdev(valid_speeds) if len(valid_speeds) > 1 else 0
        
        for speed in valid_speeds:
            # Consistent if within 1 standard deviation
            if abs(speed - avg_speed) <= std_speed:
                features.consistent_windows += 1
            else:
                features.inconsistent_windows += 1
    
    # Detect anomaly clusters
    # Cluster = 3+ paste/blur events within same window
    anomaly_threshold = 3
    anomaly_windows = []
    
    for i, window in enumerate(windows):
        paste_blur_count = (
            len([e for e in window if e.get("event_type") == "paste"]) +
            len([e for e in window if e.get("event_type") == "blur"])
        )
        
        if paste_blur_count >= anomaly_threshold:
            anomaly_windows.append(i)
    
    # Count clusters (consecutive anomalous windows)
    if anomaly_windows:
        cluster_count = 1
        for i in range(1, len(anomaly_windows)):
            if anomaly_windows[i] != anomaly_windows[i-1] + 1:
                cluster_count += 1
        
        features.anomaly_clusters = cluster_count
        
        # Find peak anomaly time
        # Use middle of most anomalous window
        max_anomaly_count = 0
        peak_window_idx = 0
        
        for i, window in enumerate(windows):
            anomaly_count = (
                len([e for e in window if e.get("event_type") in ["paste", "blur"]])
            )
            if anomaly_count > max_anomaly_count:
                max_anomaly_count = anomaly_count
                peak_window_idx = i
        
        if peak_window_idx < len(windows):
            peak_window = windows[peak_window_idx]
            if peak_window:
                features.peak_anomaly_time = peak_window[len(peak_window)//2]["timestamp"]
    
    # Detect focus pattern changes
    # Pattern change = switching between focused and unfocused states
    focus_states = []
    
    for event in events:
        if event.get("event_type") == "blur":
            focus_states.append(False)
        elif event.get("event_type") == "focus":
            focus_states.append(True)
    
    # Count state transitions
    if len(focus_states) > 1:
        changes = 0
        for i in range(1, len(focus_states)):
            if focus_states[i] != focus_states[i-1]:
                changes += 1
        features.focus_pattern_changes = changes
    
    return features


def calculate_temporal_anomaly_score(features: TemporalFeatures) -> float:
    """
    Calculate anomaly score based on temporal consistency.
    
    Higher scores indicate less consistent, more suspicious behavior.
    
    Args:
        features: TemporalFeatures dataclass
        
    Returns:
        Anomaly score between 0 and 1
    """
    score = 0.0
    
    # High behavioral variance suggests inconsistent, possibly dishonest behavior
    if features.behavior_variance_score > 100:
        score += 0.25
    
    # Many sudden behavioral shifts are suspicious
    if features.sudden_change_count > 3:
        score += 0.20
    
    # High proportion of inconsistent windows
    if features.total_time_windows > 0:
        inconsistent_ratio = features.inconsistent_windows / features.total_time_windows
        if inconsistent_ratio > 0.5:
            score += 0.20
    
    # Anomaly clustering suggests coordinated cheating moments
    if features.anomaly_clusters > 2:
        score += 0.25
    
    # Large typing speed drift may indicate different person or reference use
    if features.typing_speed_drift > 50:  # >50 WPM change
        score += 0.15
    
    return min(score, 1.0)
