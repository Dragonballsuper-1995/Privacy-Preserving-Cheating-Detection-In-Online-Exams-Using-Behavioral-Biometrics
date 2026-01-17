"""
Paste Behavior Feature Extraction

Extracts features related to paste events:
- Paste count and frequency
- Paste content size
- Correlation with pauses (paste after lookup pattern)
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class PasteFeatures:
    """Features extracted from paste behavior."""
    # Basic paste metrics
    paste_count: int = 0
    total_paste_length: int = 0
    mean_paste_length: float = 0.0
    max_paste_length: int = 0
    
    # Paste patterns
    paste_after_blur: int = 0  # Paste events shortly after tab switch
    paste_after_long_pause: int = 0  # Paste after extended pause
    
    # Timing
    first_paste_time: float = 0.0  # Time from start to first paste
    paste_frequency: float = 0.0  # Pastes per minute
    
    # Large pastes (> 100 chars - likely external content)
    large_paste_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "paste_count": self.paste_count,
            "total_paste_length": self.total_paste_length,
            "mean_paste_length": self.mean_paste_length,
            "max_paste_length": self.max_paste_length,
            "paste_after_blur": self.paste_after_blur,
            "paste_after_long_pause": self.paste_after_long_pause,
            "first_paste_time": self.first_paste_time,
            "paste_frequency": self.paste_frequency,
            "large_paste_count": self.large_paste_count,
        }


def extract_paste_features(events: List[Dict[str, Any]]) -> PasteFeatures:
    """
    Extract paste behavior features from events.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        PasteFeatures dataclass with extracted features
    """
    features = PasteFeatures()
    
    if not events:
        return features
    
    sorted_events = sorted(events, key=lambda x: x.get("timestamp", 0))
    
    # Get paste events
    paste_events = [
        e for e in sorted_events 
        if e.get("event_type") == "paste"
    ]
    
    if not paste_events:
        return features
    
    # Get blur events for correlation
    blur_events = [
        e for e in sorted_events
        if e.get("event_type") == "focus" and e.get("data", {}).get("type") == "blur"
    ]
    blur_timestamps = [e.get("timestamp", 0) for e in blur_events]
    
    # Get keydown events for pause detection
    keydown_events = [
        e for e in sorted_events
        if e.get("event_type") == "key" and e.get("data", {}).get("type") == "keydown"
    ]
    
    # Process paste events
    paste_lengths = []
    first_timestamp = sorted_events[0].get("timestamp", 0) if sorted_events else 0
    last_timestamp = sorted_events[-1].get("timestamp", 0) if sorted_events else 0
    
    for paste_event in paste_events:
        paste_time = paste_event.get("timestamp", 0)
        content_length = paste_event.get("data", {}).get("content_length", 0)
        
        paste_lengths.append(content_length)
        
        # Check for large paste
        if content_length > 100:
            features.large_paste_count += 1
        
        # Check if paste occurred shortly after blur (within 10 seconds)
        for blur_time in blur_timestamps:
            if 0 < (paste_time - blur_time) < 10000:
                features.paste_after_blur += 1
                break
        
        # Check if paste occurred after a long pause
        # Find previous keydown event
        prev_keydowns = [
            k for k in keydown_events 
            if k.get("timestamp", 0) < paste_time
        ]
        if prev_keydowns:
            last_keydown_time = max(k.get("timestamp", 0) for k in prev_keydowns)
            gap = paste_time - last_keydown_time
            if gap > 5000:  # 5 second pause before paste
                features.paste_after_long_pause += 1
    
    features.paste_count = len(paste_events)
    
    if paste_lengths:
        features.total_paste_length = sum(paste_lengths)
        features.mean_paste_length = sum(paste_lengths) / len(paste_lengths)
        features.max_paste_length = max(paste_lengths)
    
    # First paste timing
    if paste_events:
        features.first_paste_time = paste_events[0].get("timestamp", 0) - first_timestamp
    
    # Paste frequency (pastes per minute)
    total_time_minutes = (last_timestamp - first_timestamp) / 1000 / 60
    if total_time_minutes > 0:
        features.paste_frequency = features.paste_count / total_time_minutes
    
    return features


def calculate_paste_score(features: PasteFeatures) -> float:
    """
    Calculate a suspicion score based on paste behavior.
    
    Higher scores indicate more suspicious paste patterns.
    
    Args:
        features: Paste features
        
    Returns:
        Score between 0 and 1
    """
    score = 0.0
    
    # Any paste is somewhat suspicious in an exam
    if features.paste_count > 0:
        score += 0.1
    
    # Multiple pastes
    if features.paste_count >= 5:
        score += 0.3
    elif features.paste_count >= 2:
        score += 0.15
    
    # Large pastes (likely copying full answers)
    if features.large_paste_count >= 2:
        score += 0.3
    elif features.large_paste_count >= 1:
        score += 0.2
    
    # Paste after blur (classic lookup pattern)
    if features.paste_after_blur >= 2:
        score += 0.25
    elif features.paste_after_blur >= 1:
        score += 0.15
    
    # Paste after long pause
    if features.paste_after_long_pause >= 2:
        score += 0.15
    elif features.paste_after_long_pause >= 1:
        score += 0.1
    
    return min(score, 1.0)
