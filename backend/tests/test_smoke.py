"""
Simple Smoke Tests - Basic Infrastructure Validation

These tests verify that the testing infrastructure works correctly.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all modules can be imported."""
    try:
        from app.features import keystroke, hesitation, paste, focus
        from app.features.pipeline import SessionFeatures, extract_all_features
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_keystroke_dataclass():
    """Test keystroke features dataclass creation."""
    from app.features.keystroke import KeystrokeFeatures
    
    features = KeystrokeFeatures()
    assert features.total_keystrokes == 0
    assert features.typing_speed_wpm == 0.0
    
    # Test to_dict method
    feature_dict = features.to_dict()
    assert isinstance(feature_dict, dict)
    assert 'total_keystrokes' in feature_dict


def test_session_features_dataclass():
    """Test session features dataclass creation."""
    from app.features.pipeline import SessionFeatures
    
    features = SessionFeatures(session_id="test123")
    assert features.session_id == "test123"
    assert features.overall_score == 0.0
    
    # Test to_dict method
    feature_dict = features.to_dict()
    assert isinstance(feature_dict, dict)
    assert feature_dict['session_id'] == "test123"


def test_extract_all_features_empty():
    """Test that feature extraction handles empty events."""
    from app.features.pipeline import extract_all_features
    
    features = extract_all_features([], session_id="test")
    assert features.session_id == "test"
    assert features.overall_score == 0.0

 
def test_simple_calculation():
    """Very basic test that pytest is working."""
    assert 1 + 1 == 2
    assert "test".upper() == "TEST"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
