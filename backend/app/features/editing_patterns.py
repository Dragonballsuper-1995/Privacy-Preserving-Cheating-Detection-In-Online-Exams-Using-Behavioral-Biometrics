"""
Answer Editing Pattern Analysis

Analyzes how students edit their answers:
- Backspace frequency and patterns
- Correction rate (deletions vs. insertions)
- Edit velocity
- Paste-edit correlation (detecting pasted content  with minimal edits)
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import statistics


@dataclass
class EditingFeatures:
    """Features related to answer editing patterns."""
    # Backspace/deletion behavior
    backspace_count: int = 0
    backspace_ratio: float = 0.0  # Backspaces / total keystrokes
    delete_count: int = 0
    
    # Insertion vs. deletion
    total_insertions: int = 0
    total_deletions: int = 0
    correction_rate: float = 0.0  # Deletions / (insertions + deletions)
    
    # Edit velocity (characters added/deleted per minute)
    edit_velocity: float = 0.0
    
    # Editing patterns
    consecutive_backspaces: int = 0  # Max consecutive backspaces
    edit_bursts: int = 0  # Periods of rapid editing
    
    # Paste-edit correlation
    paste_events: int = 0
    edits_after_paste: int = 0
    paste_edit_ratio: float = 0.0  # Edits after paste / paste events
    
    # Text modification patterns
    avg_edit_session_length: float = 0.0
    max_text_deleted_at_once: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "backspace_count": self.backspace_count,
            "backspace_ratio": self.backspace_ratio,
            "delete_count": self.delete_count,
            "total_insertions": self.total_insertions,
            "total_deletions": self.total_deletions,
            "correction_rate": self.correction_rate,
            "edit_velocity": self.edit_velocity,
            "consecutive_backspaces": self.consecutive_backspaces,
            "edit_bursts": self.edit_bursts,
            "paste_events": self.paste_events,
            "edits_after_paste": self.edits_after_paste,
            "paste_edit_ratio": self.paste_edit_ratio,
            "avg_edit_session_length": self.avg_edit_session_length,
            "max_text_deleted_at_once": self.max_text_deleted_at_once,
        }


def extract_editing_features(events: List[Dict[str, Any]]) -> EditingFeatures:
    """
    Extract editing pattern features from events.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        EditingFeatures dataclass with extracted features
    """
    features = EditingFeatures()
    
    # Filter relevant events
    key_events = []
    paste_events = []
    
    for event in events:
        event_type = event.get("event_type")
        if event_type == "key":
            key_events.append(event)
        elif event_type == "paste":
            paste_events.append(event)
    
    if not key_events:
        return features
    
    # Track keystrokes
    total_keystrokes = 0
    backspaces = []
    deletes = []
    insertions = []
    
    consecutive_backspace_count = 0
    max_consecutive_backspaces = 0
    
    for event in key_events:
        data = event.get("data", {})
        key = data.get("key", "")
        timestamp = event.get("timestamp", 0)
        
        total_keystrokes += 1
        
        if key == "Backspace":
            features.backspace_count += 1
            backspaces.append(timestamp)
            features.total_deletions += 1
            consecutive_backspace_count += 1
            max_consecutive_backspaces = max(max_consecutive_backspaces, consecutive_backspace_count)
        
        elif key == "Delete":
            features.delete_count += 1
            deletes.append(timestamp)
            features.total_deletions += 1
            consecutive_backspace_count = 0
        
        else:
            # Regular character insertion
            insertions.append(timestamp)
            features.total_insertions += 1
            consecutive_backspace_count = 0
    
    features.consecutive_backspaces = max_consecutive_backspaces
    
    # Calculate ratios
    if total_keystrokes > 0:
        features.backspace_ratio = features.backspace_count / total_keystrokes
    
    total_edits = features.total_insertions + features.total_deletions
    if total_edits > 0:
        features.correction_rate = features.total_deletions / total_edits
    
    # Calculate edit velocity
    if key_events:
        time_span_ms = key_events[-1]["timestamp"] - key_events[0]["timestamp"]
        if time_span_ms > 0:
            time_span_min = time_span_ms / 1000 / 60
            features.edit_velocity = total_keystrokes / time_span_min
    
    # Detect edit bursts (rapid sequences of edits)
    # Edit burst = 10+ keystrokes within 2 seconds
    burst_threshold_ms = 2000
    burst_min_keys = 10
    
    i = 0
    burst_count = 0
    
    while i < len(key_events):
        # Count keys in next 2 seconds
        start_time = key_events[i]["timestamp"]
        keys_in_window = 0
        
        j = i
        while j < len(key_events) and key_events[j]["timestamp"] - start_time <= burst_threshold_ms:
            keys_in_window += 1
            j += 1
        
        if keys_in_window >= burst_min_keys:
            burst_count += 1
            i = j  # Skip past this burst
        else:
            i += 1
    
    features.edit_bursts = burst_count
    
    # Analyze paste-edit correlation
    features.paste_events = len(paste_events)
    
    if paste_events:
        # Count edits within 5 seconds after each paste
        edit_window_ms = 5000
        edits_after_paste = 0
        
        for paste_event in paste_events:
            paste_time = paste_event.get("timestamp", 0)
            
            # Count key events in the next 5 seconds
            for key_event in key_events:
                key_time = key_event.get("timestamp", 0)
                if paste_time < key_time <= paste_time + edit_window_ms:
                    edits_after_paste += 1
        
        features.edits_after_paste = edits_after_paste
        
        if features.paste_events > 0:
            features.paste_edit_ratio = edits_after_paste / features.paste_events
    
    # Calculate average edit session length
    # Edit session = continuous typing without >3s pause
    session_pause_threshold = 3000
    edit_sessions = []
    current_session_length = 0
    
    for i in range(len(key_events)):
        current_session_length += 1
        
        # Check if next event starts new session
        if i < len(key_events) - 1:
            time_gap = key_events[i+1]["timestamp"] - key_events[i]["timestamp"]
            if time_gap > session_pause_threshold:
                edit_sessions.append(current_session_length)
                current_session_length = 0
    
    if current_session_length > 0:
        edit_sessions.append(current_session_length)
    
    if edit_sessions:
        features.avg_edit_session_length = statistics.mean(edit_sessions)
    
    # Estimate max text deleted at once
    # Look for rapid sequences of backspaces
    max_rapid_backspaces = 0
    rapid_threshold = 200  # ms between backspaces
    
    current_rapid_count = 1
    for i in range(1, len(backspaces)):
        if backspaces[i] - backspaces[i-1] <= rapid_threshold:
            current_rapid_count += 1
        else:
            max_rapid_backspaces = max(max_rapid_backspaces, current_rapid_count)
            current_rapid_count = 1
    
    max_rapid_backspaces = max(max_rapid_backspaces, current_rapid_count)
    features.max_text_deleted_at_once = max_rapid_backspaces
    
    return features


def calculate_editing_anomaly_score(features: EditingFeatures) -> float:
    """
    Calculate anomaly score based on editing patterns.
    
    Higher scores indicate more suspicious editing behavior.
    
    Args:
        features: EditingFeatures dataclass
        
    Returns:
        Anomaly score between 0 and 1
    """
    score = 0.0
    
    # Very low backspace ratio suggests pasted content (honest students make mistakes)
    if features.backspace_ratio < 0.02 and features.total_insertions > 100:
        score += 0.25
    
    # Very high backspace ratio might indicate nervousness or copying errors
    if features.backspace_ratio > 0.30:
        score += 0.15
    
    # Many paste events with minimal edits = copying without understanding
    if features.paste_events > 0 and features.paste_edit_ratio < 2.0:
        score += 0.30
    
    # Large deletions at once might indicate removing pasted content
    if features.max_text_deleted_at_once > 50:
        score += 0.15
    
    # Very few edit bursts with high typing speed = possibly pasting
    if features.edit_bursts == 0 and features.edit_velocity > 200:
        score += 0.20
    
    return min(score, 1.0)
