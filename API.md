# API Documentation - Cheating Detector

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (development)  
**Last Updated:** January 18, 2026

---

## Table of Contents

1. [Authentication](#authentication)
2. [Session Management](#session-management)
3. [Event Logging](#event-logging)
4. [Analysis Endpoints](#analysis-endpoints)
5. [Dashboard & Export](#dashboard--export)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Example Workflows](#example-workflows)

---

## Authentication

### POST /api/auth/login

Authenticate a user and receive an access token.

**Request:**
```json
{
  "email": "admin@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid credentials
- `429` - Too many requests

---

## Session Management

### POST /api/sessions/create

Create a new exam session.

**Request:**
```json
{
  "exam_id": "CS101-Midterm-2026",
  "student_id": "student_12345",
  "metadata": {
    "exam_duration": 7200,
    "total_questions": 20
  }
}
```

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "exam_id": "CS101-Midterm-2026",
  "student_id": "student_12345",
  "start_time": "2026-01-18T10:00:00Z",
  "status": "active"
}
```

**Status Codes:**
- `201` - Session created
- `400` - Invalid request
- `401` - Unauthorized

---

### GET /api/sessions/{session_id}

Get session details and current status.

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "exam_id": "CS101-Midterm-2026",
  "student_id": "student_12345",
  "start_time": "2026-01-18T10:00:00Z",
  "end_time": null,
  "status": "active",
  "event_count": 1247,
  "current_risk_score": 0.32,
  "is_flagged": false
}
```

---

### POST /api/sessions/{session_id}/submit

Submit and finalize an exam session.

**Request:**
```json
{
  "answers": {
    "q1": "Answer to question 1",
    "q2": "Answer to question 2"
  },
  "completion_time": "2026-01-18T11:30:00Z"
}
```

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "status": "completed",
  "final_risk_score": 0.28,
  "is_flagged": false,
  "risk_level": "low"
}
```

---

## Event Logging

### POST /api/events/log

Log behavioral events during an exam session.

**Request:**
```json
{
  "session_id": "sess_abc123def456",
  "events": [
    {
      "event_type": "key",
      "timestamp": 1705569600000,
      "data": {
        "type": "keydown",
        "key": "a",
        "code": "KeyA"
      }
    },
    {
      "event_type": "paste",
      "timestamp": 1705569650000,
      "data": {
        "length": 127
      }
    },
    {
      "event_type": "blur",
      "timestamp": 1705569700000,
      "data": {}
    }
  ]
}
```

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "events_logged": 3,
  "status": "success"
}
```

**Event Types:**
- `key` - Keyboard events
- `mouse` - Mouse movement
- `click` - Mouse clicks
- `paste` - Paste events
- `blur` / `focus` - Window focus events
- `navigation` - Question navigation

---

### POST /api/events/batch

Log multiple event batches efficiently (recommended for production).

**Request:**
```json
{
  "batches": [
    {
      "session_id": "sess_abc123",
      "events": [...]
    },
    {
      "session_id": "sess_def456",
      "events": [...]
    }
  ]
}
```

**Response:**
```json
{
  "batches_processed": 2,
  "total_events_logged": 1523,
  "status": "success"
}
```

---

## Analysis Endpoints

### POST /api/analysis/analyze

Analyze a completed session for cheating detection.

**Request:**
```json
{
  "session_id": "sess_abc123def456",
  "options": {
    "include_features": true,
    "include_explanation": true
  }
}
```

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "analysis": {
    "final_risk_score": 0.78,
    "is_flagged": true,
    "risk_level": "high",
    "confidence": 0.92,
    "risk_factors": [
      "Content pasted: 3 paste events",
      "Tab switching detected: 5 times",
      "Extended pause: 45.2s"
    ]
  },
  "features": {
    "keystroke": {...},
    "hesitation": {...},
    "paste": {...},
    "focus": {...}
  },
  "component_scores": {
    "behavioral_score": 0.65,
    "anomaly_score": 0.82,
    "similarity_score": 0.45
  }
}
```

**Status Codes:**
- `200` - Analysis complete
- `404` - Session not found
- `422` - Session not yet completed

---

### GET /api/analysis/risk-score/{session_id}

Get real-time risk score during active exam.

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "current_risk_score": 0.42,
  "is_flagged": false,
  "risk_level": "medium",
  "updated_at": "2026-01-18T11:15:00Z"
}
```

---

### POST /api/analysis/batch

Analyze multiple sessions in bulk.

**Request:**
```json
{
  "session_ids": ["sess_abc123", "sess_def456", "sess_ghi789"]
}
```

**Response:**
```json
{
  "results": [
    {
      "session_id": "sess_abc123",
      "risk_score": 0.78,
      "is_flagged": true
    },
    ...
  ],
  "total_analyzed": 3
}
```

---

## Dashboard & Export

### GET /api/dashboard/summary

Get dashboard summary statistics.

**Query Parameters:**
- `exam_id` (optional) - Filter by exam
- `start_date` (optional) - Filter by date range
- `end_date` (optional) - Filter by date range

**Response:**
```json
{
  "total_sessions": 324,
  "active_sessions": 12,
  "completed_sessions": 312,
  "flagged_sessions": 28,
  "flagged_rate": 0.087,
  "average_risk_score": 0.23,
  "statistics": {
    "by_risk_level": {
      "low": 261,
      "medium": 35,
      "high": 15,
      "critical": 13
    }
  }
}
```

---

### GET /api/export/session/{session_id}

Export session data and analysis.

**Query Parameters:**
- `format` - `json` | `csv` | `pdf`
- `include_events` - `true` | `false`

**Response (JSON):**
```json
{
  "session": {...},
  "analysis": {...},
  "events": [...],
  "generated_at": "2026-01-18T11:30:00Z"
}
```

---

## Data Models

### Session

```typescript
interface Session {
  session_id: string;
  exam_id: string;
  student_id: string;
  start_time: string;  // ISO 8601
  end_time?: string;   // ISO 8601
  status: "active" | "completed" | "flagged";
  event_count: number;
  current_risk_score: number;
  is_flagged: boolean;
}
```

### Event

```typescript
interface Event {
  event_type: "key" | "mouse" | "click" | "paste" | "blur" | "focus" | "navigation";
  timestamp: number;  // Unix timestamp (ms)
  data: Record<string, any>;
}
```

### Analysis Result

```typescript
interface AnalysisResult {
  session_id: string;
  final_risk_score: number;      // 0-1
  is_flagged: boolean;
  risk_level: "low" | "medium" | "high" | "critical";
  confidence: number;              // 0-1
  risk_factors: string[];
  component_scores: {
    behavioral_score: number;
    anomaly_score: number;
    similarity_score: number;
  };
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid session_id format",
    "details": {
      "field": "session_id",
      "constraint": "Must match pattern: sess_[a-z0-9]+"
    }
  },
  "timestamp": "2026-01-18T11:30:00Z"
}
```

**Error Codes:**
- `VALIDATION_ERROR` - Invalid request data
- `NOT_FOUND` - Resource not found
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

---

## Rate Limiting

**Default Limits:**
- Event logging: 1000 events/minute per session
- Analysis: 10 requests/minute per API key
- Dashboard: 60 requests/minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1705569720
```

**429 Response:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 45 seconds"
  },
  "retry_after": 45
}
```

---

## Example Workflows

### Complete Exam Flow

```javascript
// 1. Create session
const session = await fetch('/api/sessions/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    exam_id: 'CS101-Midterm',
    student_id: 'student_123'
  })
});
const { session_id } = await session.json();

// 2. Log events during exam
const logEvents = async (events) => {
  await fetch('/api/events/log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, events })
  });
};

// 3.Monitor risk score in real-time (optional)
const checkRisk = async () => {
  const response = await fetch(`/api/analysis/risk-score/${session_id}`);
  const {current_risk_score} = await response.json();
  return current_risk_score;
};

// 4. Submit exam
const submit = await fetch(`/api/sessions/${session_id}/submit`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    answers: examAnswers,
    completion_time: new Date().toISOString()
  })
});

// 5. Get final analysis
const analysis = await fetch('/api/analysis/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id,
    options: { include_features: true }
  })
});
const result = await analysis.json();
console.log('Final risk:', result.analysis.final_risk_score);
```

---

### Admin Dashboard Flow

```javascript
// 1. Get summary statistics
const summary = await fetch('/api/dashboard/summary?exam_id=CS101-Midterm');
const stats = await summary.json();

// 2. Analyze flagged sessions
const flagged = stats.flagged_sessions;
const analyses = await fetch('/api/analysis/batch', {
  method: 'POST',
  body: JSON.stringify({ session_ids: flaggedSessionIds })
});

// 3. Export detailed report
const report = await fetch('/api/export/session/sess_abc123?format=pdf');
const pdf = await report.blob();
```

---

## WebSocket API (Real-Time)

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/monitor');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    session_id: 'sess_abc123'
  }));
};

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Risk update:', update.current_risk_score);
};
```

### Messages

**Subscribe to session:**
```json
{
  "action": "subscribe",
  "session_id": "sess_abc123"
}
```

**Risk updates:**
```json
{
  "type": "risk_update",
  "session_id": "sess_abc123",
  "current_risk_score": 0.45,
  "timestamp": "2026-01-18T11:30:00Z"
}
```

---

## Best Practices

1. **Batch Events:** Use `/api/events/batch` for production to reduce API calls
2. **Error Handling:** Always handle rate limits and retry with exponential backoff
3. **WebSocket for Real-Time:** Use WebSocket API for live monitoring dashboards
4. **Compression:** Enable gzip compression for large event payloads
5. **Authentication:** Always include JWT token in `Authorization: Bearer <token>` header

---

## Support

**Documentation:** https://docs.cheatingdetector.example.com  
**API Status:** https://status.cheatingdetector.example.com  
**Support Email:** api-support@example.com
