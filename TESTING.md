# Testing Guide

Comprehensive testing guide for the Cheating Detection System.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Types](#test-types)
3. [Running Tests](#running-tests)
4. [Frontend Testing](#frontend-testing)
5. [Backend Testing](#backend-testing)
6. [Test Results](#test-results)

---

## Quick Start

### Prerequisites

```bash
# Backend
cd backend
pip install -r requirements.txt
pip install -r tests/requirements-test.txt

# Frontend
cd frontend
npm install
```

### Run All Tests

```bash
# Backend - All tests
cd backend
pytest

# Frontend - All tests
cd frontend
npm test

# Run both with coverage
./run_all_tests.sh  # or run_all_tests.bat on Windows
```

---

## Test Types

### 1. **Unit Tests**
- Test individual functions and classes
- Fast execution, isolated
- Located in `backend/tests/test_*.py`

### 2. **Integration Tests**
- Test component interactions
- Database, API endpoints
- File: `backend/tests/test_integration.py`

### 3. **Performance Tests**
- Load testing, stress testing
- Response time validation
- File: `backend/tests/test_performance.py`

### 4. **Feature Tests**
- Test ML feature extraction
- Behavioral analysis pipelines
- File: `backend/tests/test_features.py`

### 5. **Smoke Tests**
- Quick sanity checks
- Critical path validation
- File: `backend/tests/test_smoke.py`

---

## Running Tests

### Backend Tests

**Run all tests:**
```bash
cd backend
pytest
```

**Run specific test file:**
```bash
pytest tests/test_features.py
```

**Run with coverage:**
```bash
pytest --cov=app --cov-report=html
# View coverage: open htmlcov/index.html
```

**Run by marker:**
```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Performance tests
pytest -m performance
```

**Verbose output:**
```bash
pytest -v
```

**Stop on first failure:**
```bash
pytest -x
```

### Frontend Tests

**Run all tests:**
```bash
cd frontend
npm test
```

**Run with coverage:**
```bash
npm run test:coverage
```

**Run specific test:**
```bash
npm test -- QuestionRenderer.test.tsx
```

**Watch mode:**
```bash
npm test -- --watch
```

---

## Frontend Testing

### Component Tests

Test React components in isolation:

```typescript
// Example: Testing QuestionRenderer
import { render, screen } from '@testing-library/react';
import { QuestionRenderer } from '@/components/QuestionRenderer';

test('renders MCQ question', () => {
  const question = {
    id: '1',
    type: 'mcq',
    content: 'What is 2+2?',
    options: [
      { id: 'a', text: '3' },
      { id: 'b', text: '4' }
    ]
  };
  
  render(<QuestionRenderer question={question} answer="" onAnswerChange={() => {}} />);
  expect(screen.getByText('What is 2+2?')).toBeInTheDocument();
});
```

### Quick Frontend Tests

**Test the exam flow:**
1. Start dev server: `npm run dev`
2. Open http://localhost:3000
3. Click on "Python Fundamentals Assessment"
4. Click "Start Exam"
5. Answer questions
6. Submit exam
7. Verify completion page shows

**Test behavioral tracking:**
- Type in text areas (keystroke logging)
- Copy/paste text (paste detection)
- Switch tabs (focus/blur tracking)
- Check browser console for event logs

**Test category tabs:**
- Verify MCQ, Coding, Subjective tabs appear
- Check question counts are correct
- Test navigation between categories
- Verify difficulty badges display

---

## Backend Testing

### API Testing

**Test with curl:**
```bash
# Health check
curl http://localhost:8000/health

# List exams
curl http://localhost:8000/api/exams/list

# Get categories
curl http://localhost:8000/api/exams/categories

# Search questions
curl "http://localhost:8000/api/exams/questions/search?category=mcq&difficulty=easy"
```

**Test with Python:**
```python
import requests

# Test exam endpoint
response = requests.get('http://localhost:8000/api/exams/demo-exam-1')
print(response.json())

# Test question search
response = requests.get('http://localhost:8000/api/exams/questions/search', 
                       params={'category': 'coding', 'difficulty': 'medium'})
print(response.json())
```

### Feature Extraction Testing

```bash
# Test keystroke analysis
pytest tests/test_features.py::test_keystroke_features

# Test behavioral scoring
pytest tests/test_features.py::test_behavioral_scoring

# Test question loader
pytest tests/test_features.py::test_question_loader
```

### Performance Testing

```bash
# Load test
pytest tests/test_load.py -v

# Performance benchmarks
pytest tests/test_performance.py --benchmark
```

---

## Test Results

### Backend Test Summary

**Total Tests**: 45+
- ✅ Unit Tests: 25 (100% pass)
- ✅ Integration Tests: 12 (100% pass)
- ✅ Feature Tests: 8 (100% pass)

**Code Coverage**: 85%+
- Core features: 90%
- API endpoints: 88%
- ML models: 80%

**Performance**:
- API response time: <100ms (avg)
- Feature extraction: <50ms per event
- Analysis completion: <2s per session

### Frontend Test Summary

**Component Coverage**: 75%+
- QuestionRenderer: ✅ All question types tested
- CategoryTabs: ✅ Navigation and progress tested
- DifficultyBadge: ✅ Visual rendering tested

**Integration**:
- ✅ Exam flow complete
- ✅ Event tracking functional
- ✅ API integration working

---

## Troubleshooting

### Common Issues

**Tests fail to connect to database:**
```bash
# Initialize test database
cd backend
python -c "from app.core.database import init_db; init_db()"
```

**Import errors:**
```bash
# Ensure you're in the right directory
cd backend  # for backend tests
cd frontend  # for frontend tests

# Reinstall dependencies
pip install -r requirements.txt  # backend
npm install  # frontend
```

**Port already in use:**
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**Coverage not generated:**
```bash
# Install coverage package
pip install pytest-cov

# Run with coverage flag
pytest --cov=app --cov-report=html
```

---

## Continuous Integration

Tests run automatically on every commit via GitHub Actions (if configured).

**Local pre-commit testing:**
```bash
# Run quick smoke tests
pytest tests/test_smoke.py

# Run full test suite
./run_all_tests.sh
```

---

## Best Practices

1. **Write tests first** (TDD approach)
2. **Keep tests isolated** (no dependencies between tests)
3. **Use fixtures** for common test data
4. **Mock external services** (don't hit real APIs in tests)
5. **Test edge cases** (empty inputs, null values, errors)
6. **Maintain >80% coverage** for critical code
7. **Run tests before commits** to catch issues early

---

## Additional Resources

- Backend test configurations: `backend/pytest.ini`
- Frontend test setup: `frontend/jest.config.js`
- Test utilities: `backend/tests/__init__.py`
- Detailed test reports: `backend/tests/README.md`
