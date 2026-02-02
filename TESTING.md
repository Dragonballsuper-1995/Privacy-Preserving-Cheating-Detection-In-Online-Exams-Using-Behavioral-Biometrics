# Testing Guide

> Test suite documentation for the Cheating Detection System

---

## Test Framework

- **Framework**: pytest 7.4+
- **HTTP Client**: httpx (for API tests)
- **Location**: `backend/tests/`
- **Requirements**: `backend/tests/requirements-test.txt`

---

## Test Files

| File | Category | Description |
|------|----------|-------------|
| `test_smoke.py` | Smoke | Basic infrastructure validation |
| `test_integration.py` | Integration | Complete ML pipeline tests |
| `test_features.py` | Unit | Feature extraction module tests |
| `test_performance.py` | Performance | Timing and throughput tests |
| `test_load.py` | Load | Stress testing endpoints |

---

## Running Tests

### Prerequisites

```bash
cd backend
pip install -r tests/requirements-test.txt
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Smoke tests only (fast)
pytest tests/test_smoke.py -v

# Integration tests
pytest tests/test_integration.py -v

# With coverage report
pytest tests/ --cov=app --cov-report=html
```

### Run Single Test

```bash
pytest tests/test_smoke.py::test_imports -v
```

---

## Current Test Coverage

### Smoke Tests (`test_smoke.py`)

| Test | What It Validates |
|------|-------------------|
| `test_imports` | All feature modules can be imported |
| `test_keystroke_dataclass` | KeystrokeFeatures dataclass creation and `to_dict()` |
| `test_session_features_dataclass` | SessionFeatures dataclass creation |
| `test_extract_all_features_empty` | Pipeline handles empty events gracefully |
| `test_simple_calculation` | pytest infrastructure works |

### Integration Tests (`test_integration.py`)

| Test | What It Validates |
|------|-------------------|
| `test_event_to_features_to_prediction` | Complete pipeline: events → features → ML prediction |
| `test_keystroke_feature_extraction` | Keystroke features extracted correctly |
| `test_hesitation_feature_extraction` | Pause detection works |
| `test_paste_feature_extraction` | Paste count and length tracking |
| `test_focus_feature_extraction` | Blur/focus event handling |
| `test_empty_events_handling` | Empty input doesn't crash |
| `test_malformed_events_handling` | Malformed events handled gracefully |
| `test_feature_dict_serialization` | Features are JSON-serializable |
| `test_high_risk_behavior_detection` | Suspicious behavior flagged |
| `test_normal_behavior_detection` | Normal behavior not flagged |

---

## Test Data Format

Tests use in-memory event dictionaries:

```python
events = [
    {
        "event_type": "keydown",
        "timestamp": 1000,
        "data": {"key": "a", "hold_time": 100}
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
    }
]

features = extract_all_features(events, session_id="test")
```

---

## Adding New Tests

### Feature Extraction Test

```python
def test_new_feature_extraction():
    """Test new feature extraction logic."""
    events = [
        {"event_type": "keydown", "timestamp": 1000, "data": {"key": "x"}}
    ]
    
    features = extract_all_features(events, session_id="test")
    feature_dict = features.to_dict()
    
    assert "your_feature" in feature_dict
    assert feature_dict["your_feature"] == expected_value
```

### API Endpoint Test (with FastAPI TestClient)

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## CI/CD Integration

Tests are designed to run in CI pipelines:

```yaml
# GitHub Actions example
- name: Run Tests
  run: |
    cd backend
    pip install -r requirements.txt
    pip install -r tests/requirements-test.txt
    pytest tests/ -v --junitxml=test-results.xml
```

---

## Known Limitations

1. **No database tests**: `TestDatabaseTransactions` class is placeholder
2. **No API contract tests**: `TestAPIContractConsistency` class is placeholder
3. **Event format sensitivity**: Some tests may show 0 values if event format doesn't match extractor expectations
