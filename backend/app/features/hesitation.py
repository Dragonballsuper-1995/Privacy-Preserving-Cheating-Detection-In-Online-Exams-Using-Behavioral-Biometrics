"""
Hesitation and Timing Feature Extraction

Extracts features related to pauses and hesitation patterns:
- Long pauses (potential lookup/cheating moments)
- Pause frequency and distribution
- Hesitation before specific actions
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import statistics


@dataclass
class HesitationFeatures:
    """Features extracted from hesitation/timing patterns."""
    # Pause detection (pauses > threshold)
    pause_count: int = 0
    total_pause_time: float = 0.0
    mean_pause_duration: float = 0.0
    max_pause_duration: float = 0.0
    
    # Pause distribution
    short_pauses: int = 0  # 2-5 seconds
    medium_pauses: int = 0  # 5-15 seconds
    long_pauses: int = 0  # > 15 seconds
    
    # Timing patterns
    total_active_time: float = 0.0
    pause_ratio: float = 0.0  # total_pause_time / total_time
    
    # First action delay
    time_to_first_keystroke: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pause_count": self.pause_count,
            "total_pause_time": self.total_pause_time,
            "mean_pause_duration": self.mean_pause_duration,
            "max_pause_duration": self.max_pause_duration,
            "short_pauses": self.short_pauses,
            "medium_pauses": self.medium_pauses,
            "long_pauses": self.long_pauses,
            "total_active_time": self.total_active_time,
            "pause_ratio": self.pause_ratio,
            "time_to_first_keystroke": self.time_to_first_keystroke,
        }


def extract_hesitation_features(
    events: List[Dict[str, Any]], 
    pause_threshold_ms: float = 2000
) -> HesitationFeatures:
    """
    Extract hesitation and timing features from events.
    
    Args:
        events: List of event dictionaries
        pause_threshold_ms: Minimum duration to consider as a pause (default 2 seconds)
        
    Returns:
        HesitationFeatures dataclass with extracted features
    """
    features = HesitationFeatures()
    
    if not events:
        return features
    
    # Get all timestamps and sort
    all_events = sorted(events, key=lambda x: x.get("timestamp", 0))
    
    if len(all_events) < 2:
        return features
    
    first_timestamp = all_events[0].get("timestamp", 0)
    last_timestamp = all_events[-1].get("timestamp", 0)
    
    # Get key events for activity detection
    key_events = [e for e in all_events if e.get("event_type") == "key"]
    keydown_events = [
        e for e in key_events 
        if e.get("data", {}).get("type") == "keydown"
    ]
    
    if keydown_events:
        # Time to first keystroke
        first_keydown = min(e.get("timestamp", 0) for e in keydown_events)
        features.time_to_first_keystroke = first_keydown - first_timestamp
    
    # Detect pauses between keydown events
    if len(keydown_events) >= 2:
        keydown_events = sorted(keydown_events, key=lambda x: x.get("timestamp", 0))
        
        pauses = []
        for i in range(1, len(keydown_events)):
            gap = keydown_events[i].get("timestamp", 0) - keydown_events[i-1].get("timestamp", 0)
            
            if gap >= pause_threshold_ms:
                pauses.append(gap)
                
                # Categorize pauses
                if gap < 5000:
                    features.short_pauses += 1
                elif gap < 15000:
                    features.medium_pauses += 1
                else:
                    features.long_pauses += 1
        
        features.pause_count = len(pauses)
        
        if pauses:
            features.total_pause_time = sum(pauses)
            features.mean_pause_duration = statistics.mean(pauses)
            features.max_pause_duration = max(pauses)
    
    # Calculate total time and pause ratio
    total_time = last_timestamp - first_timestamp
    if total_time > 0:
        features.total_active_time = total_time - features.total_pause_time
        features.pause_ratio = features.total_pause_time / total_time
    
    return features


def calculate_hesitation_score(features: HesitationFeatures) -> float:
    """
    Calculate a suspicion score based on hesitation patterns.
    
    Higher scores indicate more suspicious hesitation behavior.
    
    Args:
        features: Hesitation features
        
    Returns:
        Score between 0 and 1
    """
    score = 0.0
    
    # Many long pauses are suspicious (potential lookups)
    if features.long_pauses >= 3:
        score += 0.3
    elif features.long_pauses >= 1:
        score += 0.15
    
    # Very long maximum pause
    if features.max_pause_duration > 60000:  # > 1 minute
        score += 0.25
    elif features.max_pause_duration > 30000:  # > 30 seconds
        score += 0.15
    
    # High pause ratio (spending more time pausing than typing)
    if features.pause_ratio > 0.5:
        score += 0.2
    elif features.pause_ratio > 0.3:
        score += 0.1
    
    # Long time to first keystroke (reading/lookup before starting)
    if features.time_to_first_keystroke > 30000:  # > 30 seconds
        score += 0.15
    elif features.time_to_first_keystroke > 15000:  # > 15 seconds
        score += 0.05
    
    return min(score, 1.0)
