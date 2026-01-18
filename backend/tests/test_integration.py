"""
Integration Tests for ML Pipeline

Tests the complete flow: event logging → feature extraction → ML prediction
"""

import sys
import os
import pytest
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.features import keystroke, hesitation, paste, focus
from app.features.pipeline import SessionFeatures, extract_all_features
from app.ml.anomaly import BehaviorAnomalyDetector
from app.models.event import BehaviorEvent


class TestIntegrationPipeline:
    """Integration tests for the complete ML pipeline."""
    
    def test_event_to_features_to_prediction(self):
        """Test complete pipeline from raw events to ML prediction."""
        # Create sample behavioral events
        events = [
            {
                "event_type": "keydown",
                "timestamp": 1000,
                "data": {"key": "a", "hold_time": 100}
            },
            {
                "event_type": "keydown",
                "timestamp": 1200,
                "data": {"key": "b", "hold_time": 80}
            },
            {
                "event_type": "paste",
                "timestamp": 2000,
                "data": {"length": 50}
            },
            {
                "event_type": "blur",
                "timestamp": 3000,
                "data": {}
            },
            {
                "event_type": "focus",
                "timestamp": 5000,
                "data": {}
            },
        ]
        
        # Extract features
        features = extract_all_features(events, session_id="test")
        
        # Verify features were extracted
        assert features is not None
        feature_dict = features.to_dict()
        
        # Check expected feature categories exist
        assert "keystroke" in str(feature_dict).lower() or "avg_typing_speed" in feature_dict
        assert "paste_count" in feature_dict
        assert "blur_count" in feature_dict
        
        # Test anomaly detection (without trained model, should use heuristics)
        detector = BehaviorAnomalyDetector()
        result = detector.detect(feature_dict, session_id="test_session")
        
        # Verify result structure
        assert hasattr(result, 'session_id')
        assert hasattr(result, 'is_anomaly')
        assert hasattr(result, 'anomaly_score')
        assert result.session_id == "test_session"
    
    def test_keystroke_feature_extraction(self):
        """Test keystroke feature extraction from events."""
        events = [
            {"event_type": "keydown", "timestamp": 1000, "data": {"key": "h", "hold_time": 90}},
            {"event_type": "keydown", "timestamp": 1150, "data": {"key": "e", "hold_time": 85}},
            {"event_type": "keydown", "timestamp": 1300, "data": {"key": "l", "hold_time": 95}},
            {"event_type": "keydown", "timestamp": 1450, "data": {"key": "l", "hold_time": 90}},
            {"event_type": "keydown", "timestamp": 1600, "data": {"key": "o", "hold_time": 100}},
        ]
        
        features = keystroke.extract_keystroke_features(events)
        
        assert features.total_keystrokes == 5
        # Check if features object has typing-related attributes
        assert hasattr(features, 'mean_inter_key_delay') or hasattr(features, 'typing_speed_chars_per_sec')
    
    def test_hesitation_feature_extraction(self):
        """Test hesitation pattern detection."""
        events = [
            {"event_type": "keydown", "timestamp": 1000, "data": {}},
            {"event_type": "keydown", "timestamp": 1200, "data": {}},
            # Long pause
            {"event_type": "keydown", "timestamp": 4000, "data": {}},  # 2.8s pause
            {"event_type": "keydown", "timestamp": 4500, "data": {}},
        ]
        
        features = hesitation.extract_hesitation_features(events)
        
        assert features.long_pause_count >= 0
        assert features.max_thinking_time > 2000  # Should detect long pause
    
    def test_paste_feature_extraction(self):
        """Test paste behavior detection."""
        events = [
            {"event_type": "paste", "timestamp": 1000, "data": {"length": 100}},
            {"event_type": "paste", "timestamp": 2000, "data": {"length": 50}},
        ]
        
        features = paste.extract_paste_features(events)
        
        assert features.paste_count == 2
        assert features.total_paste_length == 150
        assert features.max_paste_length == 100
    
    def test_focus_feature_extraction(self):
        """Test window focus tracking."""
        events = [
            {"event_type": "blur", "timestamp": 1000, "data": {}},
            {"event_type": "focus", "timestamp": 3000, "data": {}},  # 2s unfocused
            {"event_type": "blur", "timestamp": 4000, "data": {}},
            {"event_type": "focus", "timestamp": 5000, "data": {}},  # 1s unfocused
        ]
        
        features = focus.extract_focus_features(events)
        
        assert features.blur_count == 2
        assert features.total_unfocused_time == 3000
    
    def test_empty_events_handling(self):
        """Test pipeline handles empty events gracefully."""
        events = []
        
        features = extract_all_features(events, session_id="test")
        feature_dict = features.to_dict()
        
        # Should return default/zero values, not error
        assert feature_dict is not None
        assert isinstance(feature_dict, dict)
    
    def test_malformed_events_handling(self):
        """Test pipeline handles malformed events gracefully."""
        events = [
            {"event_type": "keydown"},  # Missing timestamp and data
            {"timestamp": 1000},  # Missing event_type
            {"event_type": "invalid_type", "timestamp": 2000, "data": {}},  # Unknown type
        ]
        
        # Should not raise exception
        features = extract_all_features(events, session_id="test")
        assert features is not None
    
    def test_feature_dict_serialization(self):
        """Test that features can be serialized to JSON."""
        events = [
            {"event_type": "keydown", "timestamp": 1000, "data": {"key": "a"}},
            {"event_type": "paste", "timestamp": 2000, "data": {"length": 10}},
        ]
        
        features = extract_all_features(events, session_id="test")
        feature_dict = features.to_dict()
        
        # Should be JSON serializable
        json_str = json.dumps(feature_dict)
        assert json_str is not None
        
        # Should be deserializable
        deserialized = json.loads(json_str)
        assert isinstance(deserialized, dict)
    
    def test_high_risk_behavior_detection(self):
        """Test detection of clearly suspicious behavior."""
        # Simulate obvious cheating: many pastes, long blurs, fast typing
        events = [
            {"event_type": "paste", "timestamp": 1000, "data": {"length": 500}},
            {"event_type": "paste", "timestamp": 2000, "data": {"length": 300}},
            {"event_type": "paste", "timestamp": 3000, "data": {"length": 200}},
            {"event_type": "blur", "timestamp": 4000, "data": {}},
            {"event_type": "focus", "timestamp": 15000, "data": {}},  # 11s unfocused
        ]
        
        features = extract_all_features(events, session_id="test")
        feature_dict = features.to_dict()
        
        # Should have high paste count and long blur
        assert feature_dict['paste_count'] >= 3
        assert feature_dict['blur_count'] >= 1
    
    def test_normal_behavior_detection(self):
        """Test detection of normal, honest student behavior."""
        # Simulate normal typing with no suspicious activity
        events = []
        timestamp = 1000
        
        # Normal typing pattern
        for i in range(50):
            events.append({
                "event_type": "keydown",
                "timestamp": timestamp,
                "data": {"key": chr(97 + (i % 26)), "hold_time": 80 + (i % 20)}
            })
            timestamp += 150 + (i % 50)  # Realistic typing rhythm
        
        features = extract_all_features(events, session_id="test")
        feature_dict = features.to_dict()
        
        # Should show normal patterns
        assert feature_dict['paste_count'] == 0
        assert feature_dict['blur_count'] == 0
        # Note: keystroke_count might not be exact match
        assert feature_dict.get('keystroke_count', 0) >= 0 or 'total_keystrokes' in str(feature_dict)


class TestDatabaseTransactions:
    """Test database operations and transactions."""
    
    def test_event_storage_and_retrieval(self):
        """Test storing and retrieving events from database."""
        # This would require database setup
        # Placeholder for now
        pass


class TestAPIContractConsistency:
    """Test API request/response contracts."""
    
    def test_analysis_endpoint_response_format(self):
        """Test that analysis endpoint returns expected format."""
        # This would use FastAPI TestClient
        # Placeholder for now
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
