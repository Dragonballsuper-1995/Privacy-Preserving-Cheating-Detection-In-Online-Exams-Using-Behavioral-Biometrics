import pytest
import numpy as np

from app.ml.derived_features import extract_derived_features, amplifier, detect_bursts, compute_burst_bonus
from app.ml.anomaly import BehaviorAnomalyDetector, detect_anomalies, AnomalyResult
from app.ml.fusion import RiskFusionModel, compute_fused_risk, FusionResult

class TestDerivedFeatures:
    def test_amplifier(self):
        assert amplifier(0.5) == 1.0
        assert amplifier(0.7) == 1.2
        assert amplifier(0.9) == 1.5

    def test_extract_derived_features(self):
        raw_features = {
            "session_duration": 120000,
            "paste": {"paste_after_blur_count": 2, "paste_count": 5, "total_paste_length": 50},
            "focus": {"blur_count": 3, "max_absence_duration": 10000, "total_absence_time": 20000},
            "keystroke": {"mean_inter_key_delay": 200, "std_inter_key_delay": 50, "total_chars_typed": 150},
            "paste_score": 0.8,
            "focus_score": 0.5,
            "hesitation_score": 0.7
        }
        derived = extract_derived_features(raw_features)
        
        # Check computed ratios
        assert derived.paste_after_blur_ratio == 2 / 5
        assert derived.burst_density == (3 + 5) / 2.0  # 8 events / 2 mins = 4.0
        assert derived.typing_consistency == 1 - (50 / 200) # 0.75
        assert derived.paste_to_typing_ratio == 50 / (50 + 150) # 0.25
        assert derived.absence_concentration == 10000 / 20000 # 0.5
        
        # Check amplified scores
        assert derived.paste_score_amplified == 0.8 * 1.5
        assert derived.focus_score_amplified == 0.5 * 1.0
        assert round(derived.hesitation_score_amplified, 2) == round(0.7 * 1.2, 2)

    def test_detect_bursts(self):
        events = [
            {"type": "blur", "timestamp": 1000},
            {"type": "paste", "timestamp": 2000}
        ]
        bursts = detect_bursts(events, window_ms=5000)
        assert len(bursts) == 1
        assert bursts[0]["type"] == "copy_paste_burst"

        # Tab storm
        events_storm = [{"type": "blur", "timestamp": i * 1000} for i in range(6)]
        bursts_storm = detect_bursts(events_storm)
        assert any(b["type"] == "tab_switch_storm" for b in bursts_storm)

    def test_compute_burst_bonus(self):
        events = [
            {"type": "blur", "timestamp": 1000},
            {"type": "paste", "timestamp": 2000}
        ]
        bonus = compute_burst_bonus(events)
        assert bonus == 0.15


class TestAnomalyDetection:
    def test_detector_heuristic(self):
        detector = BehaviorAnomalyDetector(contamination=0.1)
        features = {
            "keystroke": {"typing_speed_wpm": 20, "mean_inter_key_delay": 300},
            "mouse": {"mean_velocity": 500},
            "focus": {"blur_count": 5},
            "paste": {"paste_count": 2, "total_paste_length": 100}
        }
        res = detector.detect(features)
        assert isinstance(res, AnomalyResult)
        assert hasattr(res, "is_anomaly")

    def test_convenience_function(self):
        res = detect_anomalies({}, "test-session")
        assert res.session_id == "test-session"
        assert res.to_dict()["session_id"] == "test-session"


class TestFusionModel:
    def test_fusion_compute_risk_weighted(self):
        # Without ML training, falls back to weighted average
        model = RiskFusionModel(use_ml=False)
        # behavioral: 0.6 * 0.5 = 0.3
        # anomaly: 0.8 * 0.3 = 0.24
        # similarity: 0.4 * 0.2 = 0.08
        # sum = 0.62
        res = model.compute_risk(0.6, 0.8, 0.4)
        assert isinstance(res, FusionResult)
        # 0.61 < flag_threshold 0.75
        assert not res.is_flagged
        assert abs(res.final_risk_score - 0.61) <= 0.01

    def test_fusion_compute_risk_flagged(self):
        model = RiskFusionModel(use_ml=False)
        res = model.compute_risk(0.9, 0.9, 0.9)
        assert res.is_flagged
        assert res.risk_level in ["high", "critical"]

    def test_convenience_function(self):
        res = compute_fused_risk(0.5, 0.5, 0.5, "test")
        assert res.session_id == "test"
        assert 0.0 <= res.to_dict()["final_risk_score"] <= 1.0

from app.ml.training import generate_honest_session, generate_cheating_session

class TestTrainingData:
    def test_generate_honest_session(self):
        session = generate_honest_session()
        events = session["events"]
        assert len(events) > 0
        
        # Honest session should have mostly keystrokes, mouse moves, and clicks
        types = set(e["type"] for e in events)
        assert "keystroke" in types or "keydown" in types
        
    def test_generate_cheating_session(self):
        session = generate_cheating_session()
        events = session["events"]
        assert len(events) > 0
        
        types = set(e["type"] for e in events)
        # Cheating session should contain suspicious events like paste or blur
        assert "paste" in types or "blur" in types or "focus" in types
