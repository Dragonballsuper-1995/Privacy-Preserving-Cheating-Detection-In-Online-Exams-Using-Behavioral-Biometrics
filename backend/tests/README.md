# Tests for Cheating Detection System

This directory contains the comprehensive test suite for the backend system.

## Test Structure

```
tests/
├── test_integration.py      # Integration tests (pipeline tests)
├── test_features.py         # Unit tests for feature extractors
├── test_performance.py      # Performance benchmarks
├── test_load.py            # Load testing with Locust
├── requirements-test.txt    # Testing dependencies
└── README.md               # This file
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r tests/requirements-test.txt
```

### Run All Tests

```bash
# From backend directory
pytest
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/test_features.py

# Integration tests only
pytest tests/test_integration.py

# Performance benchmarks
pytest tests/test_performance.py -v -s

# With coverage report
pytest --cov=app --cov-report=html
```

### Run Tests by Marker

```bash
# Only fast unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Performance tests (may take longer)
pytest -m performance
```

## Load Testing

Load testing uses Locust to simulate multiple concurrent users.

```bash
# Start Locust web UI
locust -f tests/test_load.py --host=http://localhost:8000

# Then open http://localhost:8089 in browser
# Configure: 100 users, spawn rate 10/sec, duration 5 min
```

**Targets:**
- 100+ concurrent users
- P95 response time < 500ms
- 0 failed requests under normal load

## Performance Targets

| Metric | Target | Test |
|--------|--------|------|
| Feature Extraction | < 100ms (P95) | test_performance.py |
| ML Inference | < 500ms (P95) | test_performance.py |
| End-to-End Pipeline | < 600ms (P95) | test_performance.py |
| Concurrent Users | 100+ | test_load.py |

## Test Coverage

Generate coverage report:
```bash
pytest --cov=app --cov-report=html
```

View report:
```bash
# Open htmlcov/index.html in browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
```

**Target:** > 70% code coverage

## Writing New Tests

### Unit Test Example

```python
# tests/test_myfeature.py
import pytest
from app.features import myfeature

def test_basic_functionality():
    result = myfeature.process_data([1, 2, 3])
    assert result == expected_value

def test_edge_case():
    result = myfeature.process_data([])
    assert result is not None
```

### Integration Test Example

```python
# tests/test_integration.py
def test_complete_pipeline():
    events = generate_test_events()
    features = extract_all_features(events)
    prediction = model.predict(features)
    assert prediction is not None
```

## Continuous Integration

Tests run automatically on:
- Every pull request
- Merge to develop branch
- Tagged releases

CI checks:
- ✅ All tests pass
- ✅ Code coverage > 70%
- ✅ No lint errors
- ✅ Performance benchmarks meet targets

## Troubleshooting

### Import Errors

Ensure you're running from the backend directory:
```bash
cd backend
pytest
```

### Missing Dependencies

Install test requirements:
```bash
pip install -r tests/requirements-test.txt
```

### Performance Tests Failing

Performance tests may fail on slow machines. Adjust targets in `test_performance.py` if needed.

### Load Tests Not Starting

Ensure backend is running:
```bash
uvicorn app.main:app --reload
```

Then start Locust in another terminal.

## Best Practices

1. **Test Isolation** - Each test should be independent
2. **Clear Names** - Use descriptive test function names
3. **Fast Tests** - Keep unit tests fast (< 1s each)
4. **Markers** - Use pytest markers to categorize tests
5. **Fixtures** - Use fixtures for common setup
6. **Edge Cases** - Test boundary conditions and errors

## Contact

For questions about tests, see the main README.md or implementation_plan.md.
