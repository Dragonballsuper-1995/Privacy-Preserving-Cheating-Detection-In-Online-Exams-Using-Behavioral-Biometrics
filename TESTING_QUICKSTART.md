# Testing Quick Start Guide

## Prerequisites Check

Before running tests, ensure you have:

1. **Python 3.10+** installed
2. **Virtual environment** activated
3. **Test dependencies** installed

## Step 1: Install Test Dependencies

```bash
cd backend

# Install test requirements
pip install -r tests/requirements-test.txt

# Install main requirements (if not already done)
pip install -r requirements.txt
```

## Step 2: Verify Installation

```bash
# Check pytest is installed
pytest --version

# Check coverage is installed
coverage --version
```

## Step 3: Run Tests

### Option 1: Run All Tests (Recommended First Time)

```bash
# Run all tests with verbose output
pytest -v

# Expected output: 43 tests should pass
```

### Option 2: Run Tests with Coverage

```bash
# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Open coverage report
start htmlcov/index.html  # Windows
# open htmlcov/index.html  # macOS
# xdg-open htmlcov/index.html  # Linux
```

### Option 3: Run Specific Test Files

```bash
# Run only smoke tests (quick validation)
pytest tests/test_smoke.py -v

# Run integration tests
pytest tests/test_integration.py -v

# Run feature tests
pytest tests/test_features.py -v

# Run performance tests
pytest tests/test_performance.py -v
```

### Option 4: Run by Test Markers

```bash
# Run only unit tests
pytest -m unit -v

# Run only integration tests
pytest -m integration -v

# Run only performance tests
pytest -m performance -v
```

## Step 4: Common Test Commands

```bash
# Stop on first failure (good for debugging)
pytest -x

# Show print statements
pytest -s

# Run last failed tests only
pytest --lf

# Run tests matching a pattern
pytest -k "test_keystroke" -v

# Generate XML report for CI/CD
pytest --junitxml=test-results.xml
```

## Expected Results

When all tests pass, you should see:

```
================================ test session starts =================================
platform win32 -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0
collected 43 items

tests/test_smoke.py ✓✓✓✓✓                                                    [ 11%]
tests/test_features.py ✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓                                  [ 55%]
tests/test_integration.py ✓✓✓✓✓✓✓✓✓✓✓                                        [ 81%]
tests/test_performance.py ✓✓✓✓✓✓                                              [ 95%]
tests/test_load.py ✓✓                                                         [100%]

================================ 43 passed in 12.34s =================================
```

## Troubleshooting

### Issue: Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# Install the app in development mode
pip install -e .
```

### Issue: Database Connection Errors

**Problem:** Tests fail with database connection errors

**Solution:**
```bash
# Tests use in-memory database by default
# No external database needed for most tests

# If needed, set test database URL
set DATABASE_URL=sqlite:///test.db  # Windows
export DATABASE_URL=sqlite:///test.db  # macOS/Linux
```

### Issue: Missing Models

**Problem:** `FileNotFoundError: models not found`

**Solution:**
```bash
# Train models if not present
python scripts/train_all_models.py

# Or create models directory
mkdir -p models
```

### Issue: Slow Tests

**Solution:**
```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

## What Each Test File Does

| File | Tests | Purpose |
|------|-------|---------|
| `test_smoke.py` | 5 | Quick validation that system is working |
| `test_features.py` | 19 | Unit tests for each feature extractor |
| `test_integration.py` | 11 | End-to-end pipeline tests |
| `test_performance.py` | 6 | Performance benchmarks & profiling |
| `test_load.py` | 2 | Locust load testing scenarios |

## Next Steps After Testing

Once all tests pass:

1. ✅ **Review Coverage Report** - Aim for >70%
2. ✅ **Run Performance Tests** - Verify latency targets
3. ✅ **Optional: Run Load Tests** - Test with Locust
4. ✅ **Deploy to Staging** - Use Docker Compose
5. ✅ **Run Production Tests** - Validate deployment

## Quick Reference

```bash
# The most common test command you'll use:
pytest -v --cov=app --cov-report=term-missing

# For continuous development:
pytest --watch  # (requires pytest-watch)

# For debugging:
pytest -v -s --pdb  # Drop into debugger on failure
```

## Help & Documentation

- Full testing guide: `backend/tests/README.md`
- pytest documentation: https://docs.pytest.org/
- Coverage documentation: https://coverage.readthedocs.io/

---

**Ready to test?** Run: `pytest -v` 🚀
