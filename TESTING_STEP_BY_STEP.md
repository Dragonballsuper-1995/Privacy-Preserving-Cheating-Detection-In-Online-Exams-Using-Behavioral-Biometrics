# Testing Step-by-Step Guide

## Current Status

✅ Python 3.12.8 installed  
✅ pytest and testing tools installed  
⏳ Installing backend dependencies...

## Step 1: Complete Installation (IN PROGRESS)

The system is currently installing all required dependencies. Wait for the command to complete.

## Step 2: Verify Installation

After installation completes, verify:

```bash
# Check Python version
python --version

# Check pytest
pytest --version

# Check coverage
coverage --version
```

## Step 3: Run Smoke Tests (Quick Check)

Start with the smoke tests to verify basic functionality:

```bash
cd backend
pytest tests/test_smoke.py -v
```

Expected: 5 tests should pass

## Step 4: Run All Tests

Run the complete test suite:

```bash
pytest -v
```

Expected: 43 tests total

## Step 5: Generate Coverage Report

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

This will:
- Run all tests
- Calculate code coverage
- Generate HTML report in `htmlcov/`
- Show coverage in terminal

## Common Issues & Solutions

### Issue 1: Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Fix:**
```bash
# Make sure you're in the backend directory
cd backend

# Install in development mode
pip install -e .
```

### Issue 2: Missing Models

**Error:** `FileNotFoundError: models not found`

**Fix:**
```bash
# Create models directory
mkdir models

# Train models (optional for testing)
python scripts/train_all_models.py
```

### Issue 3: Pydantic Warnings

**Warning:** Pydantic V2 warnings

**Fix:** These are just warnings and won't affect testing. Tests will still run.

## Test Execution Order

Recommended order for first-time testing:

1. **Smoke Tests** (5 tests, ~5 seconds)
   ```bash
   pytest tests/test_smoke.py -v
   ```

2. **Unit Tests** (19 tests, ~10 seconds)
   ```bash
   pytest tests/test_features.py -v
   ```

3. **Integration Tests** (11 tests, ~15 seconds)
   ```bash
   pytest tests/test_integration.py -v
   ```

4. **Performance Tests** (6 tests, ~20 seconds)
   ```bash
   pytest tests/test_performance.py -v
   ```

5. **Loadtests** (2 tests, requires Locust)
   ```bash
   pytest tests/test_load.py -v
   ```

## Expected Output

When successful:

```
================================ test session starts =================================
collected 43 items

tests/test_smoke.py::test_imports PASSED                                       [  2%]
tests/test_smoke.py::test_feature_extraction PASSED                            [  4%]
tests/test_smoke.py::test_keystroke_features PASSED                            [  7%]
tests/test_smoke.py::test_hesitation_features PASSED                           [  9%]
tests/test_smoke.py::test_paste_features PASSED                                [ 11%]
...
================================ 43 passed in 25.41s =================================
```

## Next Steps After All Tests Pass

1. ✅ Review HTML coverage report
2. ✅ Fix any failing tests
3. ✅ Run performance benchmarks
4. ✅ Test with Docker deployment
5. ✅ Run integration tests with database

## Useful Testing Commands

```bash
# Stop on first failure
pytest -x

# Show print output
pytest -s

# Run specific test
pytest tests/test_smoke.py::test_imports -v

# Run tests matching pattern
pytest -k "keystroke" -v

# Run with detailed output
pytest -vv

# Generate JUnit XML for CI/CD
pytest --junitxml=test-results.xml
```

## Monitoring Installation Progress

The current installation is downloading and installing:
- FastAPI, Uvicorn (web framework)
- SQLAlchemy, psycopg2 (database)
- scikit-learn, pandas, numpy (ML libraries)
- torch, sentence-transformers (deep learning)
- python-jose, passlib (authentication)

This may take 2-5 minutes depending on your internet speed.

---

**Next:** Wait for installation to complete, then run `pytest tests/test_smoke.py -v`
