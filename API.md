# API Reference

> Complete REST API documentation for the Cheating Detection System

**Base URL**: `http://localhost:8000`

---

## Health Check

### `GET /`

Root health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "Cheating Detection API",
  "version": "0.1.0"
}
```

### `GET /health`

Detailed health check.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "ml_models": "loaded"
}
```

---

## Events API

**Prefix**: `/api/events`

### `POST /api/events/log`

Log a batch of behavioral events from the exam frontend.

**Request Body**:
```json
{
  "session_id": "abc123-uuid",
  "events": [
    {
      "session_id": "abc123-uuid",
      "question_id": "q1",
      "event_type": "key",
      "data": {
        "type": "keydown",
        "key": "a",
        "code": "KeyA",
        "shift": false,
        "ctrl": false,
        "alt": false
      },
      "timestamp": 1700000000000
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "events_received": 50,
  "session_id": "abc123-uuid"
}
```

### `GET /api/events/session/{session_id}`

Retrieve events for a specific session.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | path | Yes | Session UUID |
| `limit` | query | No | Max events to return (default: 1000) |

**Response**:
```json
{
  "session_id": "abc123-uuid",
  "events": [...],
  "count": 500
}
```

---

## Sessions API

**Prefix**: `/api/sessions`

### `POST /api/sessions/create`

Create a new exam session.

**Request Body**:
```json
{
  "exam_id": "demo-exam-1",
  "student_id": "student-123"
}
```

**Response**:
```json
{
  "id": "session-uuid",
  "exam_id": "demo-exam-1",
  "student_id": "student-123",
  "status": "not_started",
  "started_at": null,
  "submitted_at": null,
  "current_question": 0
}
```

### `GET /api/sessions/{session_id}`

Get session details.

**Response**: Same as create response.

### `POST /api/sessions/{session_id}/start`

Start an exam session.

**Response**:
```json
{
  "message": "Session started",
  "session_id": "session-uuid"
}
```

### `POST /api/sessions/{session_id}/submit`

Submit the exam session.

**Response**:
```json
{
  "message": "Exam submitted successfully",
  "session_id": "session-uuid"
}
```

### `POST /api/sessions/{session_id}/answer`

Submit an answer for a question.

**Request Body**:
```json
{
  "question_id": "q1",
  "content": "def is_palindrome(s): ..."
}
```

**Response**:
```json
{
  "message": "Answer saved",
  "question_id": "q1"
}
```

### `GET /api/sessions/list/all`

List all sessions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | query | No | Filter by status: `not_started`, `in_progress`, `submitted`, `analyzed` |

**Response**:
```json
{
  "sessions": [...],
  "count": 15
}
```

---

## Exams API

**Prefix**: `/api/exams`

### `GET /api/exams/list`

List all available exams.

**Response**:
```json
{
  "exams": [
    {
      "id": "demo-exam-1",
      "title": "Python Fundamentals Assessment",
      "description": "Test your knowledge...",
      "duration_minutes": 30,
      "question_count": 6
    }
  ]
}
```

### `GET /api/exams/{exam_id}`

Get exam details with questions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exam_id` | path | Yes | Exam identifier |
| `include_answers` | query | No | Include correct answers (default: false) |

**Response**:
```json
{
  "id": "demo-exam-1",
  "title": "Python Fundamentals Assessment",
  "description": "...",
  "duration_minutes": 30,
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "category": "mcq",
      "difficulty": "easy",
      "content": "What is the output of: print(type([]))?",
      "points": 5,
      "options": [
        {"id": "a", "text": "<class 'tuple'>"},
        {"id": "b", "text": "<class 'list'>"}
      ]
    }
  ]
}
```

### `POST /api/exams/create`

Create a new exam.

**Request Body**:
```json
{
  "title": "New Exam",
  "description": "Description",
  "duration_minutes": 60
}
```

### `GET /api/exams/categories`

Get list of question categories.

**Response**:
```json
{
  "categories": [
    {"id": "mcq", "name": "Multiple Choice Questions", "description": "..."},
    {"id": "coding", "name": "Coding Problems", "description": "..."},
    {"id": "subjective", "name": "Subjective Questions", "description": "..."}
  ]
}
```

### `GET /api/exams/questions/search`

Search and filter questions from the question bank.

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | query | Filter by category |
| `difficulty` | query | Filter by difficulty: `easy`, `medium`, `hard` |
| `subject` | query | Filter by subject |
| `topic` | query | Filter by topic |
| `tags` | query | Comma-separated list of tags |

### `GET /api/exams/questions/random`

Get random questions from the question bank.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | query | Yes | Category to select from |
| `count` | query | No | Number of questions (default: 5) |
| `difficulty` | query | No | Filter by difficulty |
| `subject` | query | No | Filter by subject |

---

## Analysis API

**Prefix**: `/api/analysis`

### `POST /api/analysis/analyze`

Analyze a session and compute risk score.

**Request Body**:
```json
{
  "session_id": "abc123-uuid",
  "include_features": true,
  "by_question": false
}
```

**Response**:
```json
{
  "session_id": "abc123-uuid",
  "overall_score": 0.65,
  "typing_score": 0.2,
  "hesitation_score": 0.5,
  "paste_score": 0.9,
  "focus_score": 0.6,
  "is_flagged": false,
  "flag_reasons": ["High paste content ratio"],
  "features": {...}
}
```

### `POST /api/analysis/by-question`

Analyze a session with per-question breakdown.

**Response**: Array of risk scores per question.

### `GET /api/analysis/features/{session_id}`

Get detailed extracted features for a session.

### `GET /api/analysis/timeline/{session_id}`

Get a timeline of events for visualization.

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | query | Max events (default: 100) |

### `GET /api/analysis/dashboard`

Get summary statistics for all analyzed sessions.

**Response**:
```json
{
  "total_sessions": 50,
  "flagged_sessions": 12,
  "average_risk": 0.42,
  "sessions": [
    {
      "session_id": "abc123",
      "risk_score": 0.75,
      "is_flagged": true,
      "event_count": 500,
      "flag_reasons": ["Excessive pasting"],
      "scores": {
        "typing": 0.3,
        "hesitation": 0.5,
        "paste": 0.95,
        "focus": 0.7
      },
      "created_at": "2024-01-15T10:30:00Z",
      "is_simulated": false
    }
  ]
}
```

---

## Simulation API

**Prefix**: `/api/simulation`

### `POST /api/simulation/simulate`

Generate simulated exam sessions for testing.

**Request Body**:
```json
{
  "is_cheater": false,
  "count": 10,
  "question_count": 6
}
```

**Response**:
```json
{
  "generated": 10,
  "type": "honest",
  "sessions": [
    {
      "session_id": "sim-uuid",
      "is_cheater": false,
      "event_count": 250,
      "file": "session_sim-uuid.jsonl"
    }
  ]
}
```

### `POST /api/simulation/generate-training-data`

Generate a labeled training dataset.

**Request Body**:
```json
{
  "honest_count": 50,
  "cheater_count": 20
}
```

### `POST /api/simulation/train-models`

Train ML models on the generated training data.

**Response**:
```json
{
  "message": "Models trained successfully",
  "sessions_used": 70,
  "anomaly_model_path": "models/anomaly_detector.pkl",
  "fusion_model_path": "models/fusion_model.pkl"
}
```

### `GET /api/simulation/status`

Get the current status of simulation and models.

**Response**:
```json
{
  "training_data_exists": true,
  "training_info": {
    "generated_at": "2024-01-15T10:00:00Z",
    "honest_count": 50,
    "cheater_count": 20
  },
  "anomaly_model_exists": true,
  "fusion_model_exists": true,
  "event_logs_dir": "data/event_logs",
  "models_dir": "models"
}
```

---

## Evaluation API

**Prefix**: `/api/evaluation`

### `POST /api/evaluation/evaluate`

Evaluate the model on the training dataset.

**Request Body**:
```json
{
  "threshold": 0.75
}
```

**Response**:
```json
{
  "accuracy": 0.85,
  "precision": 0.80,
  "recall": 0.90,
  "f1": 0.85,
  "auc_roc": 0.92,
  "confusion_matrix": [[40, 5], [2, 18]]
}
```

### `GET /api/evaluation/optimal-threshold`

Find the optimal classification threshold.

**Response**:
```json
{
  "optimal_threshold": 0.65,
  "f1_score": 0.87,
  "metrics": {...}
}
```

### `GET /api/evaluation/report`

Generate a markdown evaluation report.

### `GET /api/evaluation/dataset-info`

Get information about the current training dataset.

**Response**:
```json
{
  "exists": true,
  "total_sessions": 70,
  "honest_sessions": 50,
  "cheater_sessions": 20,
  "balance_ratio": 2.5
}
```

---

## Error Responses

All endpoints return standard HTTP error codes:

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

**Error Response Format**:
```json
{
  "detail": "Session not found"
}
```
